

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

	dc_sign = 0
	ac_sign = 0
	AC_BITS = 10
	
	co = {}   #co for code
	for i in range(1, 64):
		co[i] = {}
		for p in range(SIZE1 + 1):
			co[i][p] = {}
	co_dc = {}	
			
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
	for i in range(21):
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
			if b[0] != 0:
				dc_sign += 1
			r = 0
			pos = 1

			for i in range(1, 64):
				if b[i] == 0:
					r += 1
					continue
		
				while (r > 15):
					pos += 16
					r -= 16

				ac_sign += 1
				pos = i + 1
				r = 0
			if r > 0:
				pass
		
	lib.fprint("\nTEST  SET:")
	lib.fprint("\nJPEG Baseline: dc symbol length:" + str(t_dc_s) + "\tdc actual bits:" + str(t_dc_b) + "\trun length bits:" + str(t_run_length_bits) + "\tactual AC bits:" + str(t_ac_b) + "\ttotal bits:" + str(t_total_bits))
	lib.fprint("\nDC sign: %s\t AC sign: %s"%(str(dc_sign), str(ac_sign)))
	return t_dc_s, t_dc_b, t_run_length_bits, t_ac_b, t_total_bits, dc_sign, ac_sign

dc_sign = 0
ac_sign = 0
if len(sys.argv) != 4:
	print "usage: python testing.py [TESTING IMAGES FOLDER] [TABLE FOLDER] [OUTPUT FILE]"
	exit()

test_folder = sys.argv[1]
out_file = open(sys.argv[2], "w")

lib.index_file = out_file
g = 0
t = 0
t_opt = 0
aa = 0
bb = 0
cc = 0
dd = 0
ee = 0
ff = 0
gg = 0
for c in range(3):
	a,b,c,d,e,f,g = calc_gain(str(c), dep1, dep2)
	aa +=a
	bb+=b
	cc+=c
	dd+=d
	ee+=e
	ff+=f
	gg+=g
	
lib.fprint("\nIn summary:")
lib.fprint("\nJPEG Baseline: dc symbol length:" + str(aa) + "\tdc actual bits:" + str(bb) + "\trun length bits:" + str(cc) + "\tactual AC bits:" + str(dd) + "\ttotal bits:" + str(ee))
lib.fprint("\nDC sign: %s\t AC sign: %s"%(str(ff), str(gg)))
lib.index_file.close()
