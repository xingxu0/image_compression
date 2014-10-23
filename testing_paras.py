

import sys, os, heapq, glob, operator, pickle, lib
from operator import itemgetter
from copy import *
from pylab import *

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


def calc_gain(comp, dep1_s, dep2_s):
	global out_file, tab_folder
	lib.fprint("Component " + comp)

	AC_BITS = 10
	
	table_folder = tab_folder + "/" + str(comp)
	lib.init_testing(comp, tab_folder)
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

	files = glob.glob(test_folder + "/*.block")	
	ratio = 0	
	lib.fprint("\tTesting: ")
	print "\t",
	
	total_opt = 0
	total_opt_dc = 0
	for f in files:
		# for optimized
		oc_dc_opt = {}
		oc_opt = {}
		
		gp_1=0 #gain part
		gp_2=0
		gp_3=0
	
		for i in range(12):
			oc_dc_opt[i] = 0
		for z in range(16):
			for b in range(1, AC_BITS + 1):
				oc_opt[(z<<4) + b] = 0
		oc_opt[0] = 0	# 0 for EOB
		oc_opt[0xf0] = 0

		ratio += 1
		print str(ratio*100/len(files)) + "%",
		sys.stdout.flush()
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
					a1,a2,a3,a4=lib.record_code(block_t, block_t_o, ii, 0xf0, pos, pos + 15, oc_t)
					oc_opt[0xf0] += 1
					pos += 16
					r -= 16
					gp_1 += lib.code[0xf0] - co[a1][a2][a3][0xf0]

				a1,a2,a3,a4=lib.record_code(block_t, block_t_o, ii, (r << 4) + b[i], pos, i, oc_t)
				if not (((r<<4) + b[i]) in co[a1][a2][a3]):
					print (r<<4) + b[i], co[a1][a2][a3]
				gp_2 += lib.code[(r<<4)+b[i]] - co[a1][a2][a3][(r<<4)+b[i]]
				lib.record_jpeg(block_t, block_t_o, ii, (r << 4) + b[i], pos, i, jpeg_t)
				oc_opt[(r << 4) + b[i]] += 1
				pos = i + 1
				r = 0
			if r > 0:
				oc_opt[0] += 1
				lib.record_jpeg(block_t, block_t_o, ii, 0, pos, 63, jpeg_t)
				a1,a2,a3,a4=lib.record_code(block_t, block_t_o, ii, 0, pos, 63, oc_t)
				gp_3 += lib.code[0] - co[a1][a2][a3][0]
		
		co_dc_opt = lib.huff_encode(oc_dc_opt, lib.bits_dc_luminance)
		co_opt = lib.huff_encode(oc_opt, lib.code)
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
	diff = array([[0]*64]*(SIZE1 + 1))
	total_gain = 0
	per = array([[0]*64]*(SIZE1 + 1))

	for i in range(1,64):
		for p in range(SIZE1 + 1):
			j[p][i-1] = 0
			yy[p][i-1] = 0
			diff[p][i-1] = 0
			per[p][i-1] = 0
			temp_gain = 0
			for pp in range(SIZE2 + 1):
				g = 0
				o = 0
				for x in co[i][p][pp]:
					g += (lib.code[x] - co[i][p][pp][x])*oc_t[i][p][pp][x]
					o += (co[i][p][pp][x])*oc_t[i][p][pp][x]				
				temp_gain += g
				total_gain += g
				j[p][i-1] += jpeg_t[i][p][pp]
				yy[p][i-1] += o
				diff[p][i-1] += jpeg_t[i][p][pp] - o
				if g != jpeg_t[i][p][pp] - o:
					lib.fprint("ERROR: test gain not equal!" +  str(g) + str(diff[p][i-1]) + str(i) + str(p) + str(pp))
				if o+g:
					lib.fprint(str(i) + " " + str(p) + " " + str(pp) + ": " + str(g) + "/" + str(o+g) + "(" +str(int(g*1.0/(o+g)*10000)/100.0) +"%)")

			if j[p][i-1]:
				per[p][i-1] = temp_gain*100.0/j[p][i-1]
				if per[p][i-1] < 0:
					lib.fprint("negative:" + str(temp_gain) + " " + str(j[p][i-1]))
					per[p][i-1] = -10		# for plotting only, it's indeed negative gain
			else:
				per[p][i-1] = 0
				
	subplot(4, 1, 1)
	pcolor(j)
	colorbar()
	ylabel('JPEG')
	subplot(4, 1, 2)
	pcolor(yy)
	colorbar()
	ylabel('ours')
	subplot(4, 1, 3)
	pcolor(diff)
	colorbar()
	ylabel('diff.')
	subplot(4, 1, 4)
	pcolor(per)
	ylabel('impro. ratio')
	colorbar()
	savefig(sys.argv[3]+"_"+comp+".png")
	close()


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

	lib.fprint("\nJPEG baseline run length bits:" + str(sum(j)) + "\tour run length bits:" + str(sum(yy)) + "\tdifference:" + str(sum(diff)) + " gain part: " + str(gp_1)+","+str(gp_2)+","+str(gp_3))
	lib.fprint("JPEG baseline DC  symbol bits:" + str(jdc) + "\tour symbol bits:" + str(jdc-gain_dc) + "\tdifference:" +str(gain_dc))
	
	lib.fprint("\nJPEG optimize run length bits:" + str(total_opt) + "\tour run length bits:" + str(sum(yy)) + "\tdifference:" + str(total_opt-sum(yy)))
	lib.fprint("JPEG optimize DC  symbol bits:" + str(total_opt_dc) + "\tour symbol bits:" + str(jdc-gain_dc) + "\tdifference:" +str(total_opt_dc-jdc+gain_dc))

	if sum(j) != t_run_length_bits:
		print "run_length_bits not equal!!"
		lib.fprint("ERROR 2 run_length_bits not equal!!")
	if t_dc_s != jdc:
		print "dc symbol not equal!!"
		lib.fprint("ERROR 2 dc symbol not equal!!")
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
g = 0
t = 0
t_opt = 0
for c in range(3):
	t_g, t_t, t_o = calc_gain(str(c), dep1, dep2)
	g += t_g
	t += t_t
	t_opt += t_o
lib.fprint("\nIn summary:")
lib.fprint("\tCompare to JPEG baseline:")
lib.fprint("\tin total " + str(t) + " bits")
lib.fprint("\tgaining " + str(g) + " bits (" + str(g*100.0/t)+"%)")
lib.fprint("\tCompare to JPEG optimize:")
lib.fprint("\tin total " + str(t_opt) + " bits")
lib.fprint("\tgaining " + str(g+t_opt-t) + " bits (" + str((g+t_opt-t)*100.0/t_opt)+"%)")

	
lib.index_file.close()
