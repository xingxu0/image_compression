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
	
def create_table(comp):
	global tab_folder
	print "Component " + comp

	AC_BITS = 10

	if comp == "0":
		code = lib.get_luminance_codes()
		lib.avg_coef = lib.avg_coef_600_0
		lib.apc_bins = lib.apc_bins_600_0
	else:
		code = lib.get_chrominance_codes()
		lib.avg_coef = lib.avg_coef_600_1
		lib.apc_bins = lib.apc_bins_600_1

	oc = {}   #oc for occur, then becomes difference
	for z in range(16):
		for b in range(1, 11):
			oc[(z<<4) + b] = 0
	oc[0] = 0	# 0 for EOB
	oc[0xf0] = 0
	pos = 1

	l_total_bits = 0
	l_run_length_bits = 0
	l_dc_s = 0
	l_dc_b = 0
	l_ac_b = 0
	
	files = glob.glob(in_folder + "/*.block")
	ratio = 0	
	print "\calculating: "
	print "\t",
	b_01 = 0
	b_02 = 0
	count_t = 0
	for f in files:
		ratio += 1
		print str(ratio*100/len(files)) + "%",
		sys.stdout.flush()
		block = lib.get_blocks_all_in_bits(f, comp)
		block_o = lib.get_blocks(f, comp)			
		for ii in range(len(block)):
			x, dc_s_bits, dc_bits, r, coef_bits = lib.get_bits_detail(block[ii], code, comp=="0")
			l_ac_b += coef_bits
			l_run_length_bits += r
			l_dc_s += dc_s_bits
			l_dc_b += dc_bits
			l_total_bits += x		
		
			# for dc symbol:
			b = block[ii]
			b_o = block_o[ii]
			#oc_dc[lib.get_previous_block(block, ii) [0]][b[0]] += 1
			r = 0
			pos = 1
			for i in range(1, 64):
				if b[i] == 0:
					r += 1
					continue
		
				while (r > 15):
					oc[0xf0] += 1
					count_t += 1
					#lib.record_code(block, block_o, ii, 0xf0, pos, pos + 15, oc)
					pos += 16
					r -= 16

				oc[(r << 4) + b[i]] += 1
				count_t += 1
				#lib.record_code(block, block_o, ii, (r << 4) + b[i], pos, i, oc)
				if r==0 and b[i]==1:
					b_01 += 1
				elif r==0 and b[i]==2:
					b_02 += 1
				pos = i + 1
				r = 0
			if r > 0:
				oc[0] += 1
				count_t += 1
				#lib.record_code(block, block_o, ii, 0, pos, 63, oc)

	print ""
	print "occurence time:"
	print "\ttotal:", count_t, "run 01:", b_01, "(", b_01*100.0/count_t, "%)", "run 02:", b_02, "(", b_02*100.0/count_t, "%)", 
	print "bits"
	print "\ttotal:", l_run_length_bits, "run 01:", b_01*2,  "(", b_01*200.0/l_run_length_bits, "%)", "run 02:", b_02*2,  "(", b_02*200.0/l_run_length_bits, "%)", 
	
	
if len(sys.argv) != 2:
	print "usage: python ratio.py [TRAINING IMAGE FOLDER]"
	exit()
	
in_folder = sys.argv[1]

for c in range(3):
	create_table(str(c))
	
#if len(sys.argv) == 1:
#	print "usage: python runsize.py size(600, 1200), component_number(0,1,2) start_learn_image(1-100), end_learn_image(1-100), end_test_image(1-100), dep. 1(0:DC, 1:avg_pre_coef, 2:avg_pre_block_coef, 3:pre_block_coef, r:last_block_eob, 5:pre_blocks_sign), dep. 2(0:DC, 1:avg_pre_coef, 2:avg_pre_block_coef, 3:pre_block_coef, 4:last_block_eob, 5:pre_blocks_sign)"
#	exit()	
