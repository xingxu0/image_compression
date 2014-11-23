

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


def calc_gain(comp, with_dc, with_sign):
	global out_file, tab_folder
	print "Component " + comp

	AC_BITS = 10
	if comp == "0":
		lib.code = lib.get_luminance_codes()
		lib.dc_code = lib.bits_dc_luminance
	else:
		lib.code = lib.get_chrominance_codes()
		lib.dc_code = lib.bits_dc_chrominance

	block = 0
	block_o = 0
	# get SIZE1_length code occurrence time for testing set
	oc_t = {}   #oc for occur, then becomes difference
	jpeg_t = {}
	t_rl_bits = 0
	t_total_bits = 0
	t_run_length_bits = 0
	t_dc_s = 0
	t_dc_b = 0
	t_ac_b = 0

			
	oc_dc_t = {}
	for i in range(12):
		oc_dc_t[i] = {}
		for j in range(12):
			oc_dc_t[i][j] = 0

	files = glob.glob(test_folder + "/*.block")	
	ratio = 0	
	
	total_opt = 0
	total_opt_dc = 0
	saving_t = 0
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
		block_t = lib.get_blocks_all_in_bits(f, comp)
		block_t_o = lib.get_blocks_with_dc_in_diff(f, comp)
	
		for ii in range(len(block_t)):
			saving = 0
			if with_sign == 0:
				x, dc_s_bits, dc_bits, r, coef_bits, saving = lib.get_bits_detail_all_positive(block_t[ii], lib.code, comp=="0")
			else:
				x, dc_s_bits, dc_bits, r, coef_bits = lib.get_bits_detail(block_t[ii], lib.code, comp=="0")
			if with_dc == 0:
				x -= dc_s_bits + dc_bits
				dc_s_bits = 0
				dc_bits = 0
			t_ac_b += coef_bits
			t_run_length_bits += r
			t_dc_s += dc_s_bits
			t_dc_b += dc_bits
			t_total_bits += x
			saving_t += saving

				
			b = block_t[ii]
			b_o = block_t_o[ii]
			if with_dc != 0:
				oc_dc_opt[b[0]] += 1
			r = 0
			pos = 1

			for i in range(1, 64):
				if b[i] == 0:
					r += 1
					continue
		
				while (r > 15):
					oc_opt[0xf0] += 1
					pos += 16
					r -= 16

				oc_opt[(r << 4) + b[i]] += 1
				pos = i + 1
				r = 0
			if r > 0:
				oc_opt[0] += 1
		
		co_dc_opt = lib.huff_encode(oc_dc_opt, lib.bits_dc_luminance)
		co_opt = lib.huff_encode(oc_opt, lib.code)
		for x in co_opt:
			total_opt += (co_opt[x])*oc_opt[x]
		for x in range(12):
			total_opt_dc += co_dc_opt[x]*oc_dc_opt[x]
		
	t_total_bits_opt = total_opt + total_opt_dc + t_dc_b + t_ac_b
	if t_dc_s + t_dc_b + t_run_length_bits + t_ac_b != t_total_bits:
		lib.fprint("test set not equal")
	print "\nTEST  SET:"
	print "\nJPEG Baseline: dc symbol length:" + str(t_dc_s) + "\tdc actual bits:" + str(t_dc_b) + "\trun length bits:" + str(t_run_length_bits) + "\tactual AC bits:" + str(t_ac_b) + "\ttotal bits:" + str(t_total_bits)
	print "\nJPEG Optimize: dc symbol length:" + str(total_opt_dc) + "\tdc actual bits:" + str(t_dc_b) + "\trun length bits:" + str(total_opt) + "\tactual AC bits:" + str(t_ac_b) + "\ttotal bits:" + str(t_total_bits_opt)
		
	print "\n\tTesting DONE"
	print "Saving due to positive:", saving_t
	return t_total_bits, t_total_bits_opt

if len(sys.argv) != 4:
	print "usage: python testing.py [TESTING IMAGES FOLDER] [WITH DC] [WITH SIGN]"
	exit()

test_folder = sys.argv[1]
with_dc = int(sys.argv[2])
with_sign = int(sys.argv[3])

g = 0
t = 0
t_opt = 0
for c in range(3):
	t_t, t_o = calc_gain(str(c), with_dc, with_sign)
	t += t_t
	t_opt += t_o
print "\nIn summary:"
print "\tCompare to JPEG baseline:"
print "\tin total " + str(t) + " bits"
print "\tCompare to JPEG optimize:"
print "\tin total " + str(t_opt) + " bits"