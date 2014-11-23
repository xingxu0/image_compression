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
	for f in files:
		ratio += 1
		print str(ratio*100/len(files)) + "%",
		sys.stdout.flush()
		b_mcu1 = 0
		b_mcu2 = 0
		if comp=="0":
			b_mcu1 = lib.get_blocks_all_in_bits(f, "1")
			b_mcu2 = lib.get_blocks_all_in_bits(f, "2")
			lib.max_pos1 = lib.get_max_pos_value_func(in_folder, "1")
			lib.max_pos2 = lib.get_max_pos_value_func(in_folder, "2")
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
			r = 0
			pos = 1
			for i in range(1, 64):
				if b[i] == 0:
					r += 1
					continue
		
				while (r > 15):
					lib.record_code(block, block_o, ii, 0xf0, pos, pos + 15, oc, b_mcu1, b_mcu2)
					pos += 16
					r -= 16

				lib.record_code(block, block_o, ii, (r << 4) + b[i], pos, i, oc, b_mcu1, b_mcu2)
				pos = i + 1
				r = 0
			if r > 0:
				lib.record_code(block, block_o, ii, 0, pos, 63, oc, b_mcu1, b_mcu2)

	if l_dc_s + l_dc_b + l_run_length_bits + l_ac_b != l_total_bits:
		lib.fprint("train set not equal")
	lib.fprint("TRAIN SET:\tdc symbol length:" + str(l_dc_s) + "\tdc actual bits:" + str(l_dc_b) + "\trun length bits:" + str(l_run_length_bits) + "\tactual AC bits:" + str(l_ac_b) + "\ttotal bits:" + str(l_total_bits))
			
		
	lib.fprint("generating DC tables...")
	for i in range(12):
		if comp == '0':
			co_dc[i] = lib.huff_encode_plus_extra(oc_dc[i], lib.bits_dc_luminance)
		else:
			co_dc[i] = lib.huff_encode_plus_extra(oc_dc[i], lib.bits_dc_chrominance)
		save_code_table(co_dc[i], oc_dc[i], "DC", i, "", table_folder)
	lib.fprint("generating AC tables...")
	for i in range(1, 64):
		#print i
		for p in range(SIZE1 + 1):
			for pp in range(SIZE2 + 1):
				co[i][p][pp] = lib.huff_encode_plus_extra(oc[i][p][pp], lib.code)
				save_code_table(co[i][p][pp], oc[i][p][pp], i, p, pp, table_folder)
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

for c in range(1):
	create_table(str(c), dep1, dep2)
	
#if len(sys.argv) == 1:
#	print "usage: python runsize.py size(600, 1200), component_number(0,1,2) start_learn_image(1-100), end_learn_image(1-100), end_test_image(1-100), dep. 1(0:DC, 1:avg_pre_coef, 2:avg_pre_block_coef, 3:pre_block_coef, r:last_block_eob, 5:pre_blocks_sign), dep. 2(0:DC, 1:avg_pre_coef, 2:avg_pre_block_coef, 3:pre_block_coef, 4:last_block_eob, 5:pre_blocks_sign)"
#	exit()	
