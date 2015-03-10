# train the images (blocks) in [INPUT FOLDER], output tables to [OUTPUT FOLDER]

import sys, copy, os, heapq, glob, operator, pickle, lib
from operator import itemgetter

def save_code_table(c, oc, i, d1, d2, table_folder):
	o = 0
	for x in oc:
		o += oc[x]
	
	if not o:
		return
	fname = table_folder + "/" + str(i)+"_"+str(d1)+"_"+str(d2)+".table"		
	pkl_file = open(fname, 'wb')
	pickle.dump(c, pkl_file)
	pkl_file.close()
	
	# also save table as human-readable	
	lib.index_file.write(str(i) + "\t" + str(d1) + "\t" + str(d2) + ":\t" + str(o) + "\n")

        f = open(table_folder + "/plain_" + str(i)+"_"+str(d1)+"_"+str(d2)+".table", "w")
        cc = sorted(c.iteritems(), key=operator.itemgetter(1))
        for x in cc:
		bits = c[x[0]]
		f.write(str(bits) + ": " + str(abs(x[0])) + "\n")
		'''
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
		'''
        f.close()
	
def create_table(comp, dep1_s, dep2_s):
	global tab_folder
	print "Component " + comp

	AC_BITS = 10
	table_folder = tab_folder + "/" + str(comp)	
	os.system("mkdir " + table_folder)
	lib.index_file = open(table_folder + "/index.txt", "w")	
	lib.init(comp, in_folder, tab_folder, dep1_s, dep2_s)
	lib.dep1, SIZE1 = lib.parse_dep(dep1_s, lib.apc_bins)
	lib.dep2, SIZE2 = lib.parse_dep(dep2_s, lib.apc_bins)
	#id_str = sys.argv[1] +"_" + comp + "_" + images_s + "_" + images_e + "[" + str(dep1) + "," + str(dep2) + "]"

	# get SIZE1_length code based on learning set
	co = {}   #co for code
	oc = {}   #oc for occur, then becomes difference
	oc_default = {}
	co_default = {}
	pos = 1

	l_total_bits = 0
	l_run_length_bits = 0
	l_dc_s = 0
	l_dc_b = 0
	l_ac_b = 0

	for i in range(1, 64):
		co[i] = {}
		oc[i] = {}
		for p in range(SIZE1 + 1):
			oc[i][p] = {}
			co[i][p] = {}
			for pp in range(SIZE2 + 1):
				oc[i][p][pp] = {}
				for z in range(16):
					for b in range(1, AC_BITS + 1):
						oc[i][p][pp][(z<<4) + b] = 0			# for one run-length, positive sign
					oc[i][p][pp][(z<<4)+15] = 0 # for +-7, independantly
					oc[i][p][pp][(z<<4)+14] = 0 # for +-6, independantly
					oc[i][p][pp][(z<<4)+13] = 0 # for +-5, independantly
					oc[i][p][pp][(z<<4)+12] = 0 # for +-3, independantly
					
				oc[i][p][pp][0] = 0	# 0 for EOB
				oc[i][p][pp][0xf0] = 0
	for z in range(16):
		for b in range(1, AC_BITS + 1):
			oc_default[(z<<4) + b] = 0			# for one run-length, positive sign
		oc_default[(z<<4)+15] = 0 # for +-7, independantly
		oc_default[(z<<4)+14] = 0 # for +-6, independantly
		oc_default[(z<<4)+13] = 0 # for +-5, independantly
		oc_default[(z<<4)+12] = 0 # for +-3, independantly
					
	oc_default[0] = 0	# 0 for EOB
	oc_default[0xf0] = 0				
	
	oc_dc = {}
	co_dc = {}
	oc_default_dc = {}
	co_default_dc = {}
	for i in range(36):
		oc_dc[i] = {}
		for j in range(23):
			oc_dc[i][j] = 0
	for j in range(23):
		oc_default_dc[j] = 0
		
	files = glob.glob(in_folder + "/*.block")
	ratio = 0
	print "\tTraining: "
	print "\t",
	for f in files:
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
			dc_de = lib.get_dc_dependency(block_o, block, ii)
			dc_diff = b_o[0]
			dc_diff_bits = b[0]
			if dc_diff < 0:
				dc_diff_bits = -dc_diff_bits
			oc_dc[dc_de][dc_diff_bits+11] += 1
			#oc_dc[lib.get_previous_blocks_coef_for_DC(block, ii)][b[0]] += 1
			r = 0
			pos = 1
			for i in range(1, 64):
				if b[i] == 0:
					r += 1
					continue
		
				while (r > 15):
					lib.record_code(block, block_o, ii, 0xf0, pos, pos + 15, oc, 0, 0)
					pos += 16
					r -= 16

				if b[i]==2:
					if abs(b_o[i])==3:
						lib.record_code(block, block_o, ii, (r << 4) + 12, pos, i, oc, 0, 0)
					else:
						lib.record_code(block, block_o, ii, (r << 4) + b[i], pos, i, oc, 0, 0)
				elif b[i]==3:
					if abs(b_o[i])==5:
						lib.record_code(block, block_o, ii, (r << 4) + 13, pos, i, oc, 0, 0)
					elif abs(b_o[i])==6:
						lib.record_code(block, block_o, ii, (r << 4) + 14, pos, i, oc, 0, 0)
					elif abs(b_o[i])==7:
						lib.record_code(block, block_o, ii, (r << 4) + 15, pos, i, oc, 0, 0)
					else:
						lib.record_code(block, block_o, ii, (r << 4) + b[i], pos, i, oc, 0, 0)
				else:
					lib.record_code(block, block_o, ii, (r << 4) + b[i], pos, i, oc, 0, 0)
				pos = i + 1
				r = 0
			if r > 0:
				lib.record_code(block, block_o, ii, 0, pos, 63, oc, 0, 0)

	if l_dc_s + l_dc_b + l_run_length_bits + l_ac_b != l_total_bits:
		lib.fprint("train set not equal")
	lib.fprint("TRAIN SET:\tdc symbol length:" + str(l_dc_s) + "\tdc actual bits:" + str(l_dc_b) + "\trun length bits:" + str(l_run_length_bits) + "\tactual AC bits:" + str(l_ac_b) + "\ttotal bits:" + str(l_total_bits))
			
		
	lib.fprint("generating DC tables...")
	for i in range(36):
		if comp == '0':
			co_dc[i] = lib.huff_encode_plus_extra_better_DC(oc_dc[i], lib.bits_dc_luminance)
		else:
			co_dc[i] = lib.huff_encode_plus_extra_better_DC(oc_dc[i], lib.bits_dc_chrominance)
		save_code_table(co_dc[i], oc_dc[i], "DC", i, "", table_folder)
		for x in oc_dc[i]:
			oc_default_dc[x] += oc_dc[i][x]
	co_default_dc = lib.huff_encode_plus_extra_better_DC(oc_default_dc, lib.bits_dc_luminance)
	save_code_table(co_default_dc, oc_default_dc, "DC", 100, "", table_folder)

	lib.fprint("generating AC tables...")
	max_len = -1
	for i in range(1, 64):
		#print i
		for p in range(SIZE1 + 1):
			for pp in range(SIZE2 + 1):
				co[i][p][pp], max_len_= lib.huff_encode_plus_extra_all(oc[i][p][pp], lib.code)
				save_code_table(co[i][p][pp], oc[i][p][pp], i, p, pp, table_folder)
				if max_len_ > max_len:
					max_len = max_len_
				for x in oc[i][p][pp]:
					oc_default[x] += oc[i][p][pp][x]
	co_default, max_len_ = lib.huff_encode_plus_extra_all(oc_default, lib.code)
	lib.fprint("default table max: " +str(max_len_))
	save_code_table(co_default, oc_default, 100,100,100,table_folder)
	lib.fprint("max length symbols: %d"%(max_len))	
	lib.index_file.close()
	print "\n\tTraining DONE"
	
if len(sys.argv) < 5:
	print "usage: python training.py [TRAINING IMAGE FOLDER] [TABLE FOLDER] [DEPENDANT 1] [DEPENDANT 2]"
	print "\t0:DC, 1:avg_pre_coef, 2:avg_pre_block_coef, 3:pre_block_coef, r:last_block_eob, 5:pre_blocks_sign"
	exit()
	
in_folder = sys.argv[1]
lib.generate_blocks(in_folder)
tab_folder = sys.argv[2]
os.system("rm -rf " + tab_folder)
os.system("mkdir " + tab_folder)

dep1 = sys.argv[3]
dep2 = sys.argv[4]

dep_file = open(tab_folder + "/dep.txt", "w")
dep_file.write(dep1 + " " + dep2 + " \n")
dep_file.close()

for c in range(3):
	create_table(str(c), dep1, dep2)
	
#if len(sys.argv) == 1:
#	print "usage: python runsize.py size(600, 1200), component_number(0,1,2) start_learn_image(1-100), end_learn_image(1-100), end_test_image(1-100), dep. 1(0:DC, 1:avg_pre_coef, 2:avg_pre_block_coef, 3:pre_block_coef, r:last_block_eob, 5:pre_blocks_sign), dep. 2(0:DC, 1:avg_pre_coef, 2:avg_pre_block_coef, 3:pre_block_coef, 4:last_block_eob, 5:pre_blocks_sign)"
#	exit()	
