# train the images (blocks) in [INPUT FOLDER], output tables to [OUTPUT FOLDER]

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


def calc_gain(comp):
	global out_file, tab_folder
	lib.fprint("Component " + comp)
	dep1_s = "1"
	dep2_s = "5"

	AC_BITS = 10

	if comp == "0":
		lib.code = lib.get_luminance_codes()
		lib.dc_code = lib.bits_dc_luminance
		lib.avg_coef = lib.avg_coef_600_0
		lib.apc_bins = lib.apc_bins_600_0
	else:
		lib.code = lib.get_chrominance_codes()
		lib.dc_code = lib.bits_dc_chrominance
		lib.avg_coef = lib.avg_coef_600_1
		lib.apc_bins = lib.apc_bins_600_1
		
	AC_BITS = 10

	lib.dep1, SIZE1 = lib.parse_dep(dep1_s, lib.apc_bins)
	lib.dep2, SIZE2 = lib.parse_dep(dep2_s, lib.apc_bins)

	table_folder = tab_folder + "/" + str(comp)

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
	for f in files:
		ratio += 1
		print str(ratio*100/len(files)) + "%",
		sys.stdout.flush()
		block_t = lib.get_blocks_all_in_bits(f, comp)
		block_t_o = lib.get_blocks(f, comp)
	
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
			r = 0
			pos = 1
			for i in range(1, 64):
				if b[i] == 0:
					r += 1
					continue
		
				while (r > 15):
					lib.record_jpeg(block_t, block_t_o, ii, 0xf0, pos, pos + 15, jpeg_t)
					lib.record_code(block_t, block_t_o, ii, 0xf0, pos, pos + 15, oc_t)
					pos += 16
					r -= 16

				lib.record_code(block_t, block_t_o, ii, (r << 4) + b[i], pos, i, oc_t)
				lib.record_jpeg(block_t, block_t_o, ii, (r << 4) + b[i], pos, i, jpeg_t)
				pos = i + 1
				r = 0
			if r > 0:
				lib.record_jpeg(block_t, block_t_o, ii, 0, pos, 63, jpeg_t)
				lib.record_code(block_t, block_t_o, ii, 0, pos, 63, oc_t)		
		
	if t_dc_s + t_dc_b + t_run_length_bits + t_ac_b != t_total_bits:
		lib.fprint("test set not equal")
	lib.fprint("TEST  SET:\tdc symbol length:" + str(t_dc_s) + "\tdc actual bits:" + str(t_dc_b) + "\trun length bits:" + str(t_run_length_bits) + "\tactual AC bits:" + str(t_ac_b) + "\ttotal bits:" + str(t_total_bits))	
	
	# x axis: position
	# y axis: SIZE1
	xx = array([[0]*64]*(SIZE1 + 1))
	j = array([[0]*64]*(SIZE1 + 1))
	yy = array([[0]*64]*(SIZE1 + 1))
	diff = array([[0]*64]*(SIZE1 + 1))
	total_gain = 0
	per = array([[0]*64]*(SIZE1 + 1))

	for i in range(1,64):
		for p in range(SIZE1 + 1):
			xx[p][i-1] = 0
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
				xx[p][i-1] += p
				j[p][i-1] += jpeg_t[i][p][pp]
				yy[p][i-1] += o
				diff[p][i-1] += jpeg_t[i][p][pp] - o
				if g != jpeg_t[i][p][pp] - o:
					lib.fprint("ERROR: test gain not equal!" +  str(g) + str(diff[p][i-1]) + str(i) + str(p) + str(pp))
			if j[p][i-1]:
				per[p][i-1] = temp_gain*100.0/j[p][i-1]
				if per[p][i-1] < 0:
					lib.fprint("negative:" + str(temp_gain) + " " + str(j[p][i-1]))
					per[p][i-1] = -10		# for plotting only, it's indeed negative gain
			else:
				per[p][i-1] = 0


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

	lib.fprint("JPEG run length bits:" + str(sum(j)) + "\tour run length bits:" + str(sum(yy)) + "\tdifference:" + str(sum(diff)))
	lib.fprint("JPEG DC  symbol bits:" + str(jdc) + "\tour symbol bits:" + str(jdc-gain_dc) + "\tdifference:" +str(gain_dc))

	if sum(j) != t_run_length_bits:
		print "run_length_bits not equal!!"
		lib.fprint("ERROR 2 run_length_bits not equal!!")
	if t_dc_s != jdc:
		print "dc symbol not equal!!"
		lib.fprint("ERROR 2 dc symbol not equal!!")
	lib.fprint("RUN LENGTH: gaining bits:" + str(total_gain) + "\ttotal bits in file:" + str(t_total_bits))
	lib.fprint("DC        : gaining bits:" + str(gain_dc) + "\ttotal bits in file:" + str(t_total_bits))
	lib.fprint("gaining " + str(total_gain + gain_dc) + " bits (" + str((total_gain+gain_dc)*100.0/t_total_bits)+"%)")
	print "\n\tTesting DONE"
	return total_gain + gain_dc, t_total_bits

if len(sys.argv) != 4:
	print "usage: python testing.py [TABLE FOLDER] [TESTING IMAGES FOLDER] [OUTPUT FILE]"
	exit()

tab_folder = sys.argv[1]
test_folder = sys.argv[2]
lib.generate_blocks(test_folder)
out_file = open(sys.argv[3], "w")
lib.index_file = out_file
g = 0
t = 0
for c in range(3):
	t_g, t_t = calc_gain(str(c))
	g += t_g
	t += t_t
lib.fprint("\nIn summary:")
lib.fprint("\tin total " + str(t) + " bits")
lib.fprint("\tgaining " + str(g) + " bits (" + str(g*100.0/t)+"%)")
	
lib.index_file.close()
