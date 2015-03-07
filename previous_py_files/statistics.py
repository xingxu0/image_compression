# train the images (blocks) in [INPUT FOLDER], output tables to [OUTPUT FOLDER]

import sys, copy, os, heapq, glob, operator, pickle, lib
from operator import itemgetter

def create_table(comp):
	global tab_folder
	print "Component " + comp

	files = glob.glob(in_folder + "/*.block")
	all_0_blocks = 0
	all_blocks = 0
	for f in files:
		block = lib.get_blocks_all_in_bits(f, comp)
		block_o = lib.get_blocks_with_dc_in_diff(f, comp)			
		for ii in range(len(block)):
			all_blocks += 1
			non_zero = False
			for i in range(1, 64):
				if block[ii][i] != 0:
					non_zero = True
					break
			if non_zero == False:
				all_0_blocks += 1
				
	print "all 0 blocks / total blocks : ", all_0_blocks, "/", all_blocks
	
if len(sys.argv) < 2:
	print "usage: python training.py [TRAINING IMAGE FOLDER]"
	exit()
	
in_folder = sys.argv[1]
lib.generate_blocks(in_folder)

for c in range(3):
	create_table(str(c))