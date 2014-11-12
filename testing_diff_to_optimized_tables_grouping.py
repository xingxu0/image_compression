
# use tables in the specified table folder, choose the best one for different cases
# for different cases, the # of the table (best table) it uses should be attached in the file
# same to testing_diff_to_optimized_table.py, but trying to group small cases together

import sys, os, heapq, glob, operator, pickle, lib
from operator import itemgetter
from copy import *
from pylab import *
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


#if len(sys.argv) == 1:
#	print "usage: python runsize.py size(600, 1200), component_number(0,1,2) start_learn_image(1-100), end_learn_image(1-100), end_test_image(1-100), dep. 1(0:DC, 1:avg_pre_coef, 2:avg_pre_block_coef, 3:pre_block_coef, r:last_block_eob, 5:pre_blocks_sign), dep. 2(0:DC, 1:avg_pre_coef, 2:avg_pre_block_coef, 3:pre_block_coef, 4:last_block_eob, 5:pre_blocks_sign)"
#	exit()

def load_code_table(i, d1, d2, table_folder):
	fname = table_folder + "/" + str(i)+"_"+str(d1)+"_"+str(d2)+".table"
	ret = {}
	if os.path.isfile(fname):
		pkl_file = open(fname, 'rb')
		ret = pickle.load(pkl_file)
		pkl_file.close()
	else:
		ret = {}
	return ret	

def load_tables(tbl_folder):
	tbls = {}
	table_number = {}
	for comp in range(3):
		tbls[comp] = []
		fs = glob.glob(tbl_folder + "/" + str(comp) + "/pool*.table")
		for f in fs:
			pkl_file = open(f, 'rb')
			tbls[comp].append((pickle.load(pkl_file), int(f[ f.find("pool") + 5 : f.find(".table")])))
			pkl_file.close()
		print comp, len(tbls[comp])
	
	return deepcopy(tbls)
	
def load_table_number(tbl_folder, comp):
	pkl_file = open(tbl_folder + "/" + str(comp) + "/table_number.table", 'rb')
	table_number = pickle.load(pkl_file)
	pkl_file.close()
	return deepcopy(table_number)

	
def get_best_table(tbls, oc):
	min_bits = -1
	for tbl in tbls:
		b = 0
		for x in oc:
			b += oc[x]*tbl[0][x]
		if min_bits == -1 or b < min_bits:
			min_bits = b
			min_tbl = deepcopy(tbl)
	return deepcopy(min_tbl)
	
	
def calc_gain(f, comp, dep1_s, dep2_s):
	global out_file, tab_folder, tbls, tbl_index_max, tbl_index_min, tbl_index_samples, total_cases, optimized_cases, table_number
	lib.fprint("Component " + comp)

	AC_BITS = 10
	
	table_folder = tab_folder + "/" + str(comp)
	lib.init_testing(comp, tab_folder, dep1_s, dep2_s)
	lib.dep1, SIZE1 = lib.parse_dep(dep1_s, lib.apc_bins)
	lib.dep2, SIZE2 = lib.parse_dep(dep2_s, lib.apc_bins)

	co = {}   #co for code
	for i in range(1, 64):
		co[i] = {}
		for p in range(SIZE1 + 1):
			co[i][p] = {}
	co_dc = {}	
			
	for i in range(12):
		co_dc[i] = load_code_table("DC", i, "", table_folder)
		if len(co_dc[i]) == 0:
			co_dc[i] = deepcopy(lib.dc_code)
	
	for i in range(1, 64):
		#print i
		for p in range(SIZE1 + 1):
			for pp in range(SIZE2 + 1):
				co[i][p][pp] = load_code_table(i, p, pp, table_folder)
				if len(co[i][p][pp]) == 0:
					co[i][p][pp] = deepcopy(lib.code)
	
	block = 0
	block_o = 0
	# get SIZE1_length code occurrence time for testing set
	oc_t = {}   #oc for occur, then becomes difference
	jpeg_t = {}
	t_rl_bits = 0
	lib.fprint("comp" + str(comp) + " testing...")
	t_total_bits = 0
	t_run_length_bits = 0
	t_dc_s = 0
	t_dc_b = 0
	t_ac_b = 0
	for i in range(1, 64):
		oc_t[i] = {}
		jpeg_t[i] = {}
		for p in range(SIZE1 + 1):
			jpeg_t[i][p] = {}
			oc_t[i][p] = {}
			for pp in range(SIZE2 + 1):
				oc_t[i][p][pp] = {}
				jpeg_t[i][p][pp] = 0
				for z in range(16):
					for b in range(1, AC_BITS + 1):
						oc_t[i][p][pp][(z<<4) + b] = 0			# for one run-length, positive sign
				oc_t[i][p][pp][0] = 0	# 0 for EOB
				oc_t[i][p][pp][0xf0] = 0	# for 16 consecutive 0, -1
			
	oc_dc_t = {}
	for i in range(12):
		oc_dc_t[i] = {}
		for j in range(12):
			oc_dc_t[i][j] = 0

	lib.fprint("\tTesting: ")
	print "\t",
	
	oc_dc_opt = {}
	oc_opt = {}
	
	for i in range(12):
		oc_dc_opt[i] = 0
	for z in range(16):
		for b in range(1, AC_BITS + 1):
			oc_opt[(z<<4) + b] = 0
	oc_opt[0] = 0	# 0 for EOB
	oc_opt[0xf0] = 0

	block_t = lib.get_blocks_all_in_bits(f, comp)
	block_t_o = lib.get_blocks_with_dc_in_diff(f, comp)

	for ii in range(len(block_t)):		
		x, dc_s_bits, dc_bits, r, coef_bits = lib.get_bits_detail(block_t[ii], lib.code, comp=="0")
		t_ac_b += coef_bits
		t_run_length_bits += r
		t_dc_s += dc_s_bits
		t_dc_b += dc_bits
		t_total_bits += x

		b = block_t[ii]
		b_o = block_t_o[ii]
		oc_dc_t[lib.get_previous_block(block_t, ii) [0]][b[0]] += 1
		oc_dc_opt[b[0]] += 1
		r = 0
		pos = 1
		for i in range(1, 64):	
			if b[i] == 0:
				r += 1
				continue
	
			while (r > 15):
				lib.record_jpeg(block_t, block_t_o, ii, 0xf0, pos, pos + 15, jpeg_t)
				lib.record_code(block_t, block_t_o, ii, 0xf0, pos, pos + 15, oc_t)
				oc_opt[0xf0] += 1
				pos += 16
				r -= 16

			lib.record_code(block_t, block_t_o, ii, (r << 4) + b[i], pos, i, oc_t)
			lib.record_jpeg(block_t, block_t_o, ii, (r << 4) + b[i], pos, i, jpeg_t)
			oc_opt[(r << 4) + b[i]] += 1
			pos = i + 1
			r = 0
		if r > 0:
			oc_opt[0] += 1
			lib.record_jpeg(block_t, block_t_o, ii, 0, pos, 63, jpeg_t)
			lib.record_code(block_t, block_t_o, ii, 0, pos, 63, oc_t)
	
	co_dc_opt = lib.huff_encode(oc_dc_opt, lib.bits_dc_luminance)
	co_opt = lib.huff_encode(oc_opt, lib.code)
	total_opt = 0
	total_opt_dc = 0
	for x in co_opt:
		total_opt += co_opt[x]*oc_opt[x]
	for x in range(12):
		total_opt_dc += co_dc_opt[x]*oc_dc_opt[x]
		
	t_total_bits_opt = total_opt + total_opt_dc + t_dc_b + t_ac_b		
	if t_dc_s + t_dc_b + t_run_length_bits + t_ac_b != t_total_bits:
		lib.fprint("test set not equal")
	lib.fprint("\nTEST  SET:")
	lib.fprint("\nJPEG Baseline: dc symbol length:" + str(t_dc_s) + "\tdc actual bits:" + str(t_dc_b) + "\trun length bits:" + str(t_run_length_bits) + "\tactual AC bits:" + str(t_ac_b) + "\ttotal bits:" + str(t_total_bits))
	lib.fprint("\nJPEG Optimize: dc symbol length:" + str(total_opt_dc) + "\tdc actual bits:" + str(t_dc_b) + "\trun length bits:" + str(total_opt) + "\tactual AC bits:" + str(t_ac_b) + "\ttotal bits:" + str(t_total_bits_opt))
	
	# x axis: position
	# y axis: SIZE1
	j = array([[0]*64]*(SIZE1 + 1))
	yy = array([[0]*64]*(SIZE1 + 1))
	diff1 = array([[0]*64]*(SIZE1 + 1))
	diff2 = array([[0]*64]*(SIZE1 + 1))
	diff = array([[0]*64]*(SIZE1 + 1))
	total_gain = 0
	per1 = array([[0]*64]*(SIZE1 + 1))
	per2 = array([[0]*64]*(SIZE1 + 1))
	per = array([[0]*64]*(SIZE1 + 1))
	
	tbl_index = array([[[-1]*64]*(SIZE1 + 1)]*(SIZE2 + 1))
	tbl_index2 = array([[0]*64]*(SIZE1 + 1))

	gaining_cases = 0
	gaining_bits = 0
	samples_x = np.arange(1,1001,1)
	samples_y = np.array([0.0]*1000)
	bits_x = np.arange(-100,3001,1)
	bits_x_n = np.arange(1, 3001, 1)
	bits_y = np.array([0.0]*3101)
	bits_y_optimized = np.array([0.0]*3000)
	samples_ = []
	gain_ = []
	
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	xxx = []
	yyy = []
	zzz = []
	sss = []
	ccc = []
	samples_gains = {}
	total_eob = 0
	total_ori_eob = 0
	opt_tbl_number = {}
	for ii in range(64):
		opt_tbl_number[ii] = {}
		for jj in range(SIZE1 + 1):
			opt_tbl_number[ii][jj] = {}
			for kk in range(SIZE2 + 1):
				opt_tbl_number[ii][jj][kk] = 0
	
	gain_per_case = array([[[-1]*(SIZE2 + 1)]*(SIZE1 + 1)]*64)
	samples_per_case = array([[[-1]*(SIZE2 + 1)]*(SIZE1 + 1)]*64)
	for i in range(1,64):
		print i
		for p in range(SIZE1 + 1):
			j[p][i-1] = 0
			yy[p][i-1] = 0
			diff[p][i-1] = 0
			per[p][i-1] = 0
			temp_gain = 0	
			
			tbls_ = 0
			for pp in range(SIZE2 + 1):
				samples = 0
				for x in oc_t[i][p][pp]:
					samples += oc_t[i][p][pp][x]
				g = 0
				o = 0				
				bits_optimized = 0
				bits_common = 0
				bits_jpeg = 0
				if samples >0 :
					samples_per_case[i][p][pp] = samples
					samples_.append(samples)
					samples_y[samples] += 1
					total_cases += 1
					tbl = ([], -1)
					tbl_optimized = get_best_table(tbls[int(comp)], oc_t[i][p][pp])
					tbl_common = (co[i][p][pp], -1)
					opt_tbl_number[i][p][pp] = tbl_optimized
					if pp % 5 ==1:
						xxx.append(i)
						yyy.append(p)
						zzz.append(pp)
						sss.append(samples)
						ccc.append(tbl_optimized[1])
					print i, p, pp, "optimized table number", tbl_optimized[1], "(common table number", table_number[i][p][pp],")"
					for x in tbl_optimized[0]:
						if x == 0:
							total_eob += tbl_common[0][0]*oc_t[i][p][pp][0]
							total_ori_eob += lib.code[0]*oc_t[i][p][pp][0]
						if oc_t[i][p][pp][x] !=0 :
							print "\tr", x>>4, "s", x&0x0f, ":", oc_t[i][p][pp][x], "opt:", tbl_optimized[0][x], "common:", tbl_common[0][x]
						bits_optimized += tbl_optimized[0][x]*oc_t[i][p][pp][x]
						bits_common += tbl_common[0][x]*oc_t[i][p][pp][x]
						bits_jpeg += lib.code[x]*oc_t[i][p][pp][x]
						g += (lib.code[x] - tbl_common[0][x])*oc_t[i][p][pp][x]
						o += (tbl_common[0][x])*oc_t[i][p][pp][x]
					print "\tsample #:", samples, "gain bits #:", bits_common - bits_optimized
					print ""
					gain_per_case[i][p][pp] = bits_common - bits_optimized
					if not samples in samples_gains:
						samples_gains[samples] = [bits_common - bits_optimized, 1]
					else:
						samples_gains[samples][0] += bits_common - bits_optimized
						samples_gains[samples][1] += 1
						
					
					gain_.append(bits_common - bits_optimized)
					bits_y[bits_common] += 1
					bits_y_optimized[bits_common - bits_optimized + 100] += 1
				if o - bits_optimized > 8:
					gaining_cases += 1
					g += o - bits_optimized - 8
					gaining_bits += o-bits_optimized-8
					o = bits_optimized + 8
				j[p][i-1] += bits_jpeg
				diff1[p][i-1] += bits_common - bits_optimized
				diff2[p][i-1] += bits_jpeg - bits_common
				temp_gain += g
				total_gain += g
				yy[p][i-1] += o
				diff[p][i-1] += jpeg_t[i][p][pp] - o				
				if g != jpeg_t[i][p][pp] - o:
					lib.fprint("ERROR: test gain not equal!" +  str(g) + str(diff[p][i-1]) + str(i) + str(p) + str(pp))
				if o+g:
					#lib.fprint(str(i) + " " + str(p) + " " + str(pp) + ": " + str(g) + "/" + str(o+g) + "(" +str(int(g*1.0/(o+g)*10000)/100.0) +"%)")
					pass
			
			if tbls_ != 0:
				tbl_index2[p][i-1] = tbl_index2[p][i-1]*1.0/tbls_

			if j[p][i-1] and j[p][i-1]-diff2[p][i-1] != 0:
				per1[p][i-1] = diff1[p][i-1]*100.0/(j[p][i-1]-diff2[p][i-1])
				per2[p][i-1] = diff2[p][i-1]*100.0/j[p][i-1]
				if per[p][i-1] < 0:
					lib.fprint("negative:" + str(temp_gain) + " " + str(j[p][i-1]))
					per[p][i-1] = -10		# for plotting only, it's indeed negative gain
			else:
				per1[p][i-1] = 0
				per2[p][i-1] = 0
				
	# below grouping results
	x1 = []
	y1 = []
	z1 = []
	s1 = []
	c1 = []
	xxxxx = []
	yyyyy = []
	sssss = []
	c = 0
	while(True):
		xx1 = []
		yy1 = []
		zz1 = []
		ss1 = []
		cc1 = []

		c+=1
		_gain = 0
		_samples = 0
		_cases = 0
		found = False
		for i in range(1,64):
			for p in range(SIZE1 + 1):
				for pp in range(SIZE2 + 1):
					if gain_per_case[i][p][pp] != -1:
						found = True
						opt = opt_tbl_number[i][p][pp]
						common = table_number[i][p][pp]
						oc = oc_t[i][p][pp]
						xx1.append(i)
						yy1.append(p)
						zz1.append(pp)
						ss1.append(1)
						cc1.append(c)
						_gain = gain_per_case[i][p][pp]
						_cases += 1
						
		if found ==False:
			break
		for i in range(1,64):
			for p in range(SIZE1 + 1):
				for pp in range(SIZE2 + 1):
					if gain_per_case[i][p][pp] == -1 or abs(opt_tbl_number[i][p][pp] - opt) > 50:
						continue
					new = 0
					old = 0
					oc_new = deepcopy(oc)
					for x in oc_t[i][p][pp]:
						new += oc_t[i][p][pp][x]*opt[0][x]
						old += oc_t[i][p][pp][x]*co[i][p][pp][x]
						oc_new[x] += oc_t[i][p][pp][x]
					if old > new:
						oc = deepcopy(oc_new)
						_gain += old - new
						_samples += samples[i][p][pp]
						#opt = get_best_table(tbl[int(comp)], oc)
						_cases += 1
						xx1.append(i)
						yy1.append(p)
						zz1.append(pp)
						ss1.append(1)
						cc1.append(c)
						gain_per_case[i][p][pp] = -1
		if len(xx1) > 5:
			x1 += xx1
			y1 += yy1
			z1 += zz1
			s1 += ss1
			c1 += cc1
		else:
			c -= 1
			
		xxxxx.append(_samples)
		yyyyy.append(_gain)
		sssss.append(_cases)
	# above grouping results
	ax.scatter(x1,y1,z1,s=s1, c=c1)
	fig.savefig(sys.argv[3]+"_"+ f[f.rfind("/")+1:] +"_group_3d_" + comp + ".png")
	close()
	
	subplot(1,1,1)
	scatter(xxxxx, yyyyy, s=sssss)
	xlabel("# of samples")
	ylabel("gain bits of optimized (b)")
	savefig(sys.argv[3]+"_"+ f[f.rfind("/")+1:] +"_"+comp+"_group_samples_gain.png")
	close()	
				
	ax.scatter(xxx,yyy,zzz,s=sss, c=ccc)
	fig.savefig(sys.argv[3]+"_"+ f[f.rfind("/")+1:] +"_3d_" + comp + ".png")
	
	subplot(1,1,1)
	xxxx = []
	yyyy = []
	ssss = []
	for x in samples_gains:
		xxxx.append(x)
		yyyy.append(samples_gains[x][0]*1.0/samples_gains[x][1])
		ssss.append(samples_gains[x][1])
	scatter(xxxx, yyyy, s=ssss)
	xlabel("# of samples")
	ylabel("gain bits of optimized (b)")
	savefig(sys.argv[3]+"_"+ f[f.rfind("/")+1:] +"_"+comp+"_samples_gain.png")
	close()
				
	subplot(5, 1, 1)
	pcolor(j)
	colorbar()
	ylabel('JPEG')
	subplot(5, 1, 2)
	pcolor(diff2)
	colorbar()
	ylabel('gain of common table')
	subplot(5, 1, 3)
	pcolor(per2)
	colorbar()
	ylabel('impro. ratio of common table')
	subplot(5, 1, 4)
	pcolor(diff1)
	colorbar()
	ylabel('gain of optimized table')
	subplot(5, 1, 5)
	pcolor(per1)
	colorbar()
	ylabel('impro. ratio of optimized table')
	savefig(sys.argv[3]+"_"+ f[f.rfind("/")+1:] +"_"+comp+".png")
	close()
	
	samples_y /= 	samples_y.sum()
	bits_y /= bits_y.sum()
	bits_y_optimized /= bits_y_optimized.sum()
	c_samples_y = np.cumsum(samples_y)
	c_bits_y = np.cumsum(bits_y)
	c_bits_y_optimized = np.cumsum(bits_y_optimized)
	
	print gaining_cases, gaining_bits
	subplot(2,2,1)
	plot(samples_x[1:100], c_samples_y[1:100])
	ylabel('samples')
	subplot(2,2,2)
	plot(bits_x_n[1:300], c_bits_y[1:300], '-b')
	ylabel('bits')
	subplot(2,2,3)
	plot(bits_x[90:115], c_bits_y_optimized[90:115], '--r')
	ylabel('diff bits')
	subplot(2,2,4)
	scatter(samples_, gain_)
	ylabel('sample x gain')	
	savefig(sys.argv[3]+"_"+ f[f.rfind("/")+1:] +"_"+comp+"_distribution.png")
	


	gain_dc = 0
	jdc = 0
	for i in range(12):
		for ii in range(12):
			if comp == "0":
				gain_dc += oc_dc_t[i][ii]*(lib.bits_dc_luminance[ii] - co_dc[i][ii])
				jdc += oc_dc_t[i][ii]*lib.bits_dc_luminance[ii]
			else:
				gain_dc += oc_dc_t[i][ii]*(lib.bits_dc_chrominance[ii] - co_dc[i][ii])
				jdc += oc_dc_t[i][ii]*lib.bits_dc_chrominance[ii]

	lib.fprint("\nJPEG baseline run length bits:" + str(sum(j)) + "\tour run length bits:" + str(sum(yy)) + "\tdifference:" + str(sum(diff)))
	lib.fprint("JPEG baseline DC  symbol bits:" + str(jdc) + "\tour symbol bits:" + str(jdc-gain_dc) + "\tdifference:" +str(gain_dc))
	
	lib.fprint("\nJPEG optimize run length bits:" + str(total_opt) + "\tour run length bits:" + str(sum(yy)) + "\tdifference:" + str(total_opt-sum(yy)))
	lib.fprint("JPEG optimize DC  symbol bits:" + str(total_opt_dc) + "\tour symbol bits:" + str(jdc-gain_dc) + "\tdifference:" +str(total_opt_dc-jdc+gain_dc))

	if sum(j) != t_run_length_bits:
		print "run_length_bits not equal!!"
		lib.fprint("ERROR 2 run_length_bits not equal!!")
	if t_dc_s != jdc:
		print "dc symbol not equal!!"
		lib.fprint("ERROR 2 dc symbol not equal!!")
	lib.fprint("\nEOB bits:" + str(total_eob) + "   ori bits:" + str(total_ori_eob))
	lib.fprint("\nCompare to JPEG Baseline:")
	lib.fprint("RUN LENGTH: gaining bits:" + str(total_gain) + "\ttotal bits in file:" + str(t_total_bits))
	lib.fprint("DC        : gaining bits:" + str(gain_dc) + "\ttotal bits in file:" + str(t_total_bits))
	lib.fprint("gaining " + str(total_gain + gain_dc) + " bits (" + str((total_gain+gain_dc)*100.0/t_total_bits)+"%)")
	
	lib.fprint("\nCompare to JPEG Optimize:")
	lib.fprint("RUN LENGTH: gaining bits:" + str(total_gain+total_opt-sum(j)) + "\ttotal bits in file:" + str(t_total_bits_opt))
	lib.fprint("DC        : gaining bits:" + str(gain_dc+total_opt_dc-jdc) + "\ttotal bits in file:" + str(t_total_bits_opt))
	lib.fprint("gaining " + str(total_gain+total_opt-sum(j)+gain_dc+total_opt_dc-jdc) + " bits (" + str((total_gain+total_opt-sum(j)+gain_dc+total_opt_dc-jdc)*100.0/t_total_bits_opt)+"%)")
	
	print "\n\tTesting DONE"
	return total_gain + gain_dc, t_total_bits, t_total_bits_opt

if len(sys.argv) != 4:
	print "usage: python testing.py [TESTING IMAGES FOLDER] [TABLE FOLDER] [OUTPUT FILE]"
	exit()

tab_folder = sys.argv[2]
test_folder = sys.argv[1]
lib.generate_blocks(test_folder)
out_file = open(sys.argv[3], "w")

dep1, dep2 = lib.get_deps_from_file(tab_folder + "/dep.txt")
print dep1, dep2
lib.index_file = out_file

files = glob.glob(test_folder + "/*.block")

tbls = load_tables(tab_folder)

total_g = 0
total_t = 0
total_opt = 0
tbl_index_max = array([[[[-1]*64]*(20 + 1)]*(26 + 1)]*3)
tbl_index_min = array([[[[10000000]*64]*(20 + 1)]*(26 + 1)]*3)
tbl_index_samples = array([[[[0]*64]*(20 + 1)]*(26 + 1)]*3)
total_cases = 0
optimized_cases = 0
for f in files:
	g = 0
	t = 0
	t_opt = 0
	for c in range(1): #(3):
		total_cases = 0
		table_number = load_table_number(tab_folder, c)
		optimized_cases = 0
		t_g, t_t, t_o = calc_gain(f, str(c), dep1, dep2)
		print "cases: ", optimized_cases, total_cases
		g += t_g
		t += t_t
		t_opt += t_o
		total_g += t_g
		total_t += t_t
		total_opt += t_o
	lib.fprint(f + ": \n\t"+ "baseline bits: " + str(t) + "   gaining " + str(g) + "   bits (" + str(g*100.0/t)+"%) " + "   optimize bits:" + str(t_opt) + "   gaining " + str(g+t_opt-t) + "   bits (" + str((g+t_opt-t)*100.0/t_opt)+"%)")

lib.fprint("finally: \n\t" + "baseline bits:"+ str(total_t) + "   gaining " + str(total_g) + "   bits (" + str(total_g*100.0/total_t)+"%)" + "   optimize bits:"+ str(total_opt) + "   gaining " + str(total_g+total_opt-total_t) + "   bits (" + str((total_g+total_opt-total_t)*100.0/total_opt)+"%)")

close()
'''
for c in range(3):
	for i in range(26 + 1):
		tmp = array([[-1]*64]*(20 + 1))
		tmp_samples = array([[0]*64]*(20 + 1))
		for j in range(1, 64):
			for k in range(20 + 1):
				tmp[k][j] = tbl_index_max[c][i][k][j] - tbl_index_min[c][i][k][j]
				tmp_samples[k][j] = tbl_index_samples[c][i][k][j]
				if tmp[k][j] <-10000000:
					tmp[k][j] = -1
		subplot(2, 1, 1)
		pcolor(tmp)
		ylabel('range')
		colorbar()
		subplot(2, 1, 2)
		pcolor(tmp_samples)
		ylabel('samples')
		colorbar()
		savefig(sys.argv[3]+"_range_"+ str(c) + "_" + str(i) +".png")
		close()
'''		

lib.index_file.close()
