# train the images (blocks) in [INPUT FOLDER], output tables to [OUTPUT FOLDER]

import sys, copy, os, heapq, glob, operator, pickle, lib
from operator import itemgetter
from pylab import *

def create_final_table(oc, table_folder):
	for i in range(tbl+1):
		o = 0
		for x in oc[i]:
			o += oc[i][x]
		if not o:
			continue
		c = lib.huff_encode_plus_extra(oc[i], lib.code)			
		fname = table_folder + "/pool_" + str(i)+".table"		
		pkl_file = open(fname, 'wb')
		pickle.dump(c, pkl_file)
		pkl_file.close()
		f = open(table_folder + "/plain_final_" + str(i) + ".table", "w")
		cc = sorted(oc[i].iteritems(), key=operator.itemgetter(1), reverse = True)
		for x in cc:
		        if x[0] == 0 or x[0] == 0xf0:
		                neg = 0
		        elif x[0] > 0:
		                neg = 1
		        else:
		                neg = -1
		        bits = c[x[0]]
		        num = abs(x[0])
		        size = num & 0x0f
		        run = num >> 4
		        if o:
		                prob = str(x[1]) + " " + str(x[1]*100.0/o)
		        else:
		                prob = "0 100"
		        if neg == -1:
		                f.write("-")
		        elif neg == 1:
		                f.write("+")
		        else:
		                f.write(" ")
		        f.write(str(run) + "/" + str(size) + ": \t" + str(bits) + "\t ( " + str(prob) +"% )\n")
		f.close()

def save_code_table(c, oc, i, d1, d2, table_folder, tbl_value):
	o = 0
	for x in oc:
		o += oc[x]
	if not o:
		return
	'''
	fname = table_folder + "/" + str(i)+"_"+str(d1)+"_"+str(d2)+".table"		
	pkl_file = open(fname, 'wb')
	pickle.dump(c, pkl_file)
	pkl_file.close()
	'''
	# also save table as human-readable	
	lib.index_file.write(str(i) + "\t" + str(d1) + "\t" + str(d2) + ":\t" + str(o) + "\n")
	
	# calculate a value for this table
	if tbl_value != None:
		v = 0
		for x in oc:
			size = abs(x) & 0x0f
			run = abs(x) >> 4
			if run == 0:
				v += oc[x]*1.0/o*size
		tbl_value[i][d1][d2] = v			

	'''
        f = open(table_folder + "/plain_" + str(i)+"_"+str(d1)+"_"+str(d2)+".table", "w")
        cc = sorted(oc.iteritems(), key=operator.itemgetter(1), reverse = True)
        for x in cc:
                if x[0] == 0 or x[0] == 0xf0:
                        neg = 0
                elif x[0] > 0:
                        neg = 1
                else:
                        neg = -1
                bits = c[x[0]]
                num = abs(x[0])
                size = num & 0x0f
                run = num >> 4
                if o:
                        prob = str(x[1]) + " " + str(x[1]*100.0/o)
                else:
                        prob = "0 100"
                if neg == -1:
                        f.write("-")
                elif neg == 1:
                        f.write("+")
                else:
                        f.write(" ")
                f.write(str(run) + "/" + str(size) + ": \t" + str(bits) + "\t ( " + str(prob) +"% )\n")
        f.close()
        '''

def get_bits(co, oc):
	b = 0
	for x in oc:
		b += oc[x]*lib.code[x]
	return b

def create_table(comp, dep1_s, dep2_s):
	global tab_folder
	#print "Component " + comp
	AC_BITS = 10
	table_folder = tab_folder + "/" + str(comp)	
	os.system("mkdir " + table_folder)
	lib.index_file = open(table_folder + "/index.txt", "w")	
	lib.init(comp, in_folder, tab_folder)
	lib.dep1, SIZE1 = lib.parse_dep(dep1_s, lib.apc_bins)
	lib.dep2, SIZE2 = lib.parse_dep(dep2_s, lib.apc_bins)
	#id_str = sys.argv[1] +"_" + comp + "_" + images_s + "_" + images_e + "[" + str(dep1) + "," + str(dep2) + "]"

	# get SIZE1_length code based on learning set
	co = {}   #co for code
	oc = {}   #oc for occur, then becomes difference
	jpeg_t = {}
	tbl_value = array([[[0.0]*(SIZE2 + 1)]*(SIZE1 + 1)]*64) # give a value for each table, larger means potentially larger coefficients.
	tbl_number = array([[[-1]*(SIZE2 + 1)]*(SIZE1 + 1)]*64) # give a value for each table, larger means potentially larger coefficients.	
	pos = 1

	l_total_bits = 0
	l_run_length_bits = 0
	l_dc_s = 0
	l_dc_b = 0
	l_ac_b = 0
	
	for i in range(1, 64):
		co[i] = {}
		oc[i] = {}
		jpeg_t[i] = {}		
		for p in range(SIZE1 + 1):
			oc[i][p] = {}
			co[i][p] = {}
			jpeg_t[i][p] = {}
			for pp in range(SIZE2 + 1):
				oc[i][p][pp] = {}
				jpeg_t[i][p][pp] = 0
				tbl_value[i][p][pp] = -100.0
				for z in range(16):
					for b in range(1, AC_BITS + 1):
						oc[i][p][pp][(z<<4) + b] = 0			# for one run-length, positive sign
				oc[i][p][pp][0] = 0	# 0 for EOB
				oc[i][p][pp][0xf0] = 0
	oc_dc = {}
	co_dc = {}
	for i in range(12):
		oc_dc[i] = {}
		for j in range(12):
			oc_dc[i][j] = 0
	
	files = glob.glob(in_folder + "/*.block")
	ratio = 0
	print "\tTraining: "
	print "\t",
	
	total_opt = 0
	total_opt_dc = 0	
	for f in files:
		# for optimized
		oc_dc_opt = {}
		oc_opt = {}
	
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
		block = lib.get_blocks_all_in_bits(f, comp)
		block_o = lib.get_blocks_with_dc_in_diff(f, comp)			
		for ii in range(len(block)):
			x, dc_s_bits, dc_bits, r, coef_bits = lib.get_bits_detail(block[ii], lib.code, comp=="0")
			l_ac_b += coef_bits
			l_run_length_bits += r
			l_dc_s += dc_s_bits
			l_dc_b += dc_bits
			l_total_bits += x		
		
			# for dc symbol:
			b = block[ii]
			b_o = block_o[ii]
			oc_dc[lib.get_previous_block(block, ii) [0]][b[0]] += 1
			oc_dc_opt[b[0]] += 1
			r = 0
			pos = 1
			for i in range(1, 64):
				if b[i] == 0:
					r += 1
					continue
		
				while (r > 15):
					lib.record_code(block, block_o, ii, 0xf0, pos, pos + 15, oc)
					lib.record_jpeg(block, block_o, ii, 0xf0, pos, pos + 15, jpeg_t)
					oc_opt[0xf0] += 1					
					pos += 16
					r -= 16

				lib.record_code(block, block_o, ii, (r << 4) + b[i], pos, i, oc)
				lib.record_jpeg(block, block_o, ii, (r << 4) + b[i], pos, i, jpeg_t)
				oc_opt[(r << 4) + b[i]] += 1			
				pos = i + 1
				r = 0
			if r > 0:
				oc_opt[0] += 1
				lib.record_code(block, block_o, ii, 0, pos, 63, oc)
				lib.record_jpeg(block, block_o, ii, 0, pos, 63, jpeg_t)
		
		co_dc_opt = lib.huff_encode(oc_dc_opt, lib.bits_dc_luminance)
		co_opt = lib.huff_encode(oc_opt, lib.code)
		for x in co_opt:
			total_opt += co_opt[x]*oc_opt[x]
		for x in range(12):
			total_opt_dc += co_dc_opt[x]*oc_dc_opt[x]
		
	t_total_bits_opt = total_opt + total_opt_dc + l_dc_b + l_ac_b					

	if l_dc_s + l_dc_b + l_run_length_bits + l_ac_b != l_total_bits:
		lib.fprint("train set not equal")
	lib.fprint("TRAIN SET:\tdc symbol length:" + str(l_dc_s) + "\tdc actual bits:" + str(l_dc_b) + "\trun length bits:" + str(l_run_length_bits) + "\tactual AC bits:" + str(l_ac_b) + "\ttotal bits:" + str(l_total_bits))
			
		
	lib.fprint("generating DC tables...")
	for i in range(12):
		if comp == '0':
			co_dc[i] = lib.huff_encode(oc_dc[i], lib.bits_dc_luminance)
		else:
			co_dc[i] = lib.huff_encode(oc_dc[i], lib.bits_dc_chrominance)
		save_code_table(co_dc[i], oc_dc[i], "DC", i, "", table_folder, None)
	lib.fprint("generating AC tables...")
	for i in range(1, 64):
		#print i
		for p in range(SIZE1 + 1):
			for pp in range(SIZE2 + 1):
				co[i][p][pp] = lib.huff_encode(oc[i][p][pp], lib.code)
				save_code_table(co[i][p][pp], oc[i][p][pp], i, p, pp, table_folder, tbl_value)
	print "\n\tTraining DONE"
	
	# x axis: position
	# y axis: SIZE1
	vv = array([[0.0]*64]*(SIZE1 + 1))
	t_tbls = 0
	for i in range(1,64):
		for p in range(SIZE1 + 1):
			t_t = 0
			for pp in range(SIZE2 + 1):
				if tbl_value[i][p][pp] >= 0:
					vv[p][i-1] += tbl_value[i][p][pp]
					t_t += 1
			if t_t>0:		
				vv[p][i-1] *= 1.0/t_t
			else:
				vv[p][i-1] = -1.0
	max_v = tbl_value.max()
	min_v = 0
	print max_v, min_v
	step = (max_v - min_v)*1.0/tbl/20.0
	bins = [0]*(tbl*20 + 1)
	separators = []
	for i in range(tbl*20):
		separators.append([min_v + i*step])
	for i in range(1,64):
		for p in range(SIZE1 + 1):
			for pp in range(SIZE2 + 1):
				if tbl_value[i][p][pp] >=0:
					b = get_bits(co[i][p][pp], oc[i][p][pp])
					bins[int((tbl_value[i][p][pp]-min_v)/step)] += b
					t_tbls += b
	sep = lib.bin_separator(bins, separators, tbl, t_tbls)
	
	for i in range(1,64):
		for p in range(SIZE1 + 1):
			for pp in range(SIZE2 + 1):
				if tbl_value[i][p][pp] >= 0:
					bin = -1
					for x in range(len(sep)):
						if tbl_value[i][p][pp] < sep[x]:
							bin = x
							break
					if bin == -1:
						bin = len(sep)
					tbl_number[i][p][pp] = bin
	subplot(1, 1, 1)
	pcolor(vv)
	colorbar()
	ylabel('Tbl Value')
	savefig(sys.argv[3]+"_tbl_value_"+comp+".png")
	close()
	
	oc_final_table = {}
	for i in range(tbl+1):
		oc_final_table[i] = {}
	for i in range(1,64):
		for p in range(SIZE1 + 1):
			for pp in range(SIZE2 + 1):
				tbl_ = tbl_number[i][p][pp]
				if tbl_ != -1:
					for x in oc[i][p][pp]:
						if x in oc_final_table[tbl_]:
							oc_final_table[tbl_][x] += oc[i][p][pp][x]
						else:
							oc_final_table[tbl_][x] = oc[i][p][pp][x]
	co_final = {}	
	for i in range(tbl+1):
		o = 0
		for x in oc_final_table[i]:
			o += oc_final_table[i][x]
		if not o:
			continue
		co_final[i] = lib.huff_encode(oc_final_table[i], lib.code)								
	create_final_table(oc_final_table, table_folder)
	
	# testing...
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
				tbl_ = tbl_number[i][p][pp]
				if tbl_ == -1:
					continue
				for x in co_final[tbl_]:
					g += (lib.code[x] - co_final[tbl_][x])*oc[i][p][pp][x]
					o += (co_final[tbl_][x])*oc[i][p][pp][x]				
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
	savefig("specialized_" + sys.argv[3]+"_"+comp+"_"+str(tbl)+".png")
	close()


	gain_dc = 0
	jdc = 0
	for i in range(12):
		for ii in range(12):
			if comp == "0":
				gain_dc += oc_dc[i][ii]*(lib.bits_dc_luminance[ii] - co_dc[i][ii])
				jdc += oc_dc[i][ii]*lib.bits_dc_luminance[ii]
			else:
				gain_dc += oc_dc[i][ii]*(lib.bits_dc_chrominance[ii] - co_dc[i][ii])
				jdc += oc_dc[i][ii]*lib.bits_dc_chrominance[ii]

	lib.fprint("\nJPEG baseline run length bits:" + str(sum(j)) + "\tour run length bits:" + str(sum(yy)) + "\tdifference:" + str(sum(diff)))
	lib.fprint("JPEG baseline DC  symbol bits:" + str(jdc) + "\tour symbol bits:" + str(jdc-gain_dc) + "\tdifference:" +str(gain_dc))
	
	lib.fprint("\nJPEG optimize run length bits:" + str(total_opt) + "\tour run length bits:" + str(sum(yy)) + "\tdifference:" + str(total_opt-sum(yy)))
	lib.fprint("JPEG optimize DC  symbol bits:" + str(total_opt_dc) + "\tour symbol bits:" + str(jdc-gain_dc) + "\tdifference:" +str(total_opt_dc-jdc+gain_dc))

	if sum(j) != l_run_length_bits:
		print "run_length_bits not equal!!"
		lib.fprint("ERROR 2 run_length_bits not equal!!")
	if l_dc_s != jdc:
		print "dc symbol not equal!!"
		lib.fprint("ERROR 2 dc symbol not equal!!")
	lib.fprint("\nCompare to JPEG Baseline:")
	lib.fprint("RUN LENGTH: gaining bits:" + str(total_gain) + "\ttotal bits in file:" + str(l_total_bits))
	lib.fprint("DC        : gaining bits:" + str(gain_dc) + "\ttotal bits in file:" + str(l_total_bits))
	lib.fprint("gaining " + str(total_gain + gain_dc) + " bits (" + str((total_gain+gain_dc)*100.0/l_total_bits)+"%)")
	
	lib.fprint("\nCompare to JPEG Optimize:")
	lib.fprint("RUN LENGTH: gaining bits:" + str(total_gain+total_opt-sum(j)) + "\ttotal bits in file:" + str(t_total_bits_opt))
	lib.fprint("DC        : gaining bits:" + str(gain_dc+total_opt_dc-jdc) + "\ttotal bits in file:" + str(t_total_bits_opt))
	lib.fprint("gaining " + str(total_gain+total_opt-sum(j)+gain_dc+total_opt_dc-jdc) + " bits (" + str((total_gain+total_opt-sum(j)+gain_dc+total_opt_dc-jdc)*100.0/t_total_bits_opt)+"%)")
	
	print "\n\tTesting DONE"
	return total_gain + gain_dc, l_total_bits, t_total_bits_opt	
	
if len(sys.argv) < 5:
	print "usage: python training.py [TRAINING IMAGE FOLDER] [TABLE FOLDER] [DEPENDANT 1] [DEPENDANT 2] [TABLE number]"
	print "\t0:DC, 1:avg_pre_coef, 2:avg_pre_block_coef, 3:pre_block_coef, r:last_block_eob, 5:pre_blocks_sign"
	exit()
	
in_folder = sys.argv[1]
lib.generate_blocks(in_folder)
tab_folder = sys.argv[2]
os.system("rm -rf " + tab_folder)
os.system("mkdir " + tab_folder)

dep1 = sys.argv[3]
dep2 = sys.argv[4]
tbl = int(sys.argv[5])

dep_file = open(tab_folder + "/dep.txt", "w")
dep_file.write(dep1 + " " + dep2 + " \n")
dep_file.close()


g = 0
t = 0
t_opt = 0
for c in range(3):
	t_g, t_t, t_o = create_table(str(c), dep1, dep2)
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
	
#if len(sys.argv) == 1:
#	print "usage: python runsize.py size(600, 1200), component_number(0,1,2) start_learn_image(1-100), end_learn_image(1-100), end_test_image(1-100), dep. 1(0:DC, 1:avg_pre_coef, 2:avg_pre_block_coef, 3:pre_block_coef, r:last_block_eob, 5:pre_blocks_sign), dep. 2(0:DC, 1:avg_pre_coef, 2:avg_pre_block_coef, 3:pre_block_coef, 4:last_block_eob, 5:pre_blocks_sign)"
#	exit()	
