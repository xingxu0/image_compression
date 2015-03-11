

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

	co_dc = {}	
	co_dc_old = {}
			
	for i in range(12):
		co_dc[i] = load_code_table("DC", i, "", table_folder)
		co_dc_old[i] = load_code_table("DC_old", i, "", table_folder)
		if len(co_dc[i]) == 0:
			co_dc[i] = deepcopy(lib.dc_code)

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
			
	oc_dc_t = {}
	oc_dc_new = {}
	for i in range(12):
		oc_dc_t[i] = {}
		oc_dc_new[i] = {}
		for j in range(12):
			oc_dc_t[i][j] = 0
			oc_dc_new[i][j] = 0

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
		block_t_o = lib.get_blocks_with_dc_in_diff_with_threshold(f, comp)
	
		for ii in range(len(block_t)):				
			b = block_t[ii]
			b_o = block_t_o[ii]
			oc_dc_t[lib.get_previous_block(block_t, ii) [0]][b[0]] += 1
			oc_dc_new[lib.get_previous_block(block_t_o, ii) [0]][b_o[0]] += 1
			oc_dc_opt[b[0]] += 1
			r = 0
			pos = 1

		
		co_dc_opt = lib.huff_encode(oc_dc_opt, lib.bits_dc_luminance)
		co_opt = lib.huff_encode(oc_opt, lib.code)
		for x in range(12):
			total_opt_dc += (co_dc_opt[x] + x)*oc_dc_opt[x]
	
	old_dc = 0
	new_dc = 0
	jdc = 0
	print co_dc[0]
	print co_dc_old[0]
	for i in range(12):
		for ii in range(12):
			if oc_dc_new[i][ii] != 0:
				new_dc += oc_dc_new[i][ii]*(co_dc[i][ii] + 1 + ii)
			if oc_dc_t[i][ii] != 0:
				old_dc += oc_dc_t[i][ii]*(co_dc_old[i][ii] + ii)
			
			if comp == "0":
				jdc += oc_dc_t[i][ii]*(lib.bits_dc_luminance[ii] + ii)
			else:
				jdc += oc_dc_t[i][ii]*(lib.bits_dc_chrominance[ii] + ii)

	#lib.fprint("\nJPEG baseline run length bits:" + str(sum(j)) + "\tour run length bits:" + str(sum(yy)) + "\tdifference:" + str(sum(diff)) + " gain part: " + str(gp_1)+","+str(gp_2)+","+str(gp_3))
	lib.fprint("\nJPEG baseline DC  symbol bits:" + str(jdc) + "\tour symbol bits:" + str(new_dc) + "\told scheme:" + str(old_dc))
	lib.fprint("JPEG optimize DC  symbol bits:" + str(total_opt_dc) + "\tour symbol bits:" + str(new_dc) + "\told scheme:" + str(old_dc))
	
if len(sys.argv) != 4:
	print "usage: python testing.py [TESTING IMAGES FOLDER] [TABLE FOLDER] [OUTPUT FILE]"
	exit()

tab_folder = sys.argv[2]
test_folder = sys.argv[1]
lib.generate_blocks(test_folder)
out_file = open(sys.argv[3], "w")

lib.index_file = out_file
g = 0
t = 0
t_opt = 0
for c in range(3):
	calc_gain(str(c), 0, 0)
	
lib.index_file.close()
