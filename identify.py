

import sys, os, heapq, glob, operator, pickle, lib
from operator import itemgetter
from copy import *
from pylab import *

def calc_gain(comp, dep1_s, dep2_s):
	global out_file, tab_folder
	if comp == "0":
		lib.code = lib.get_luminance_codes()
	else:
		lib.code = lib.get_chrominance_codes()
	AC_BITS = 10
	
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
	
	files = glob.glob(test_folder + "/*.block")	
	ratio = 0	
	print "\t",
	
	total_opt = 0
	total_opt_dc = 0
	total_eob = 0
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
		total_eob = co_opt[0]*oc_opt[0]
		for x in co_opt:
			total_opt += co_opt[x]*oc_opt[x]
		for x in range(12):
			total_opt_dc += co_dc_opt[x]*oc_dc_opt[x]
		
	t_total_bits_opt = total_opt + total_opt_dc + t_dc_b + t_ac_b		
	if t_dc_s + t_dc_b + t_run_length_bits + t_ac_b != t_total_bits:
		print "test set not equal"
	print "\nTEST  SET:"
	print "\nJPEG Baseline: dc symbol length:" + str(t_dc_s) + "\tdc actual bits:" + str(t_dc_b) + "\trun length bits:" + str(t_run_length_bits) + "\tactual AC bits:" + str(t_ac_b) + "\ttotal bits:" + str(t_total_bits)
	print "\nJPEG Optimize: dc symbol length:" + str(total_opt_dc) + "\tdc actual bits:" + str(t_dc_b) + "\trun length bits:" + str(total_opt) + "\tactual AC bits:" + str(t_ac_b) + "\ttotal bits:" + str(t_total_bits_opt) + "\teob bits:"+str(total_eob)
	
if len(sys.argv) != 2:
	print "usage: python testing.py [TESTING IMAGES FOLDER]"
	exit()

test_folder = sys.argv[1]
lib.generate_blocks(test_folder)
g = 0
t = 0
t_opt = 0
for c in range(3):
	calc_gain(str(c), 0, 0)