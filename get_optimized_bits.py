import lib, sys, copy, os, heapq
from operator import itemgetter
from pylab import *
sys.path.insert(0, '../huff_coding')
from prob_to_table_memory import *
import operator
			
def check_startpoint(b, i):    # determine is there a SIZE1-length code; most of the cases, if previou number is non-zero, then it's a SIZE1-length code; however, if previous is 16x 0s, it's still a new start
	if (i>1 and b[i-1]) or i==1:
		return True
	f = True
	for ii in range(i, 64):
		if b[ii]:
			f = False
			break
	if f:
		return False
	z = 0
	for ii in range(i - 1, 0, -1):
		if b[ii]:
			break
		z += 1
	if z % 16 == 0:
		return True
	return False

def get_avg_pre_coef(b, i):
	if i==1:
		return min(10, b[0])
	t = 0
	ma = 0
	for x in range(1, i):
		t += b[x]
		ma += avg_coef[x]
	return scale(t*1.0/ma, i)

def scale(f, i):
	global apc_bins
	for x in range(len(apc_bins[i])):
		if f <= apc_bins[i][x]:
			return x
	return len(apc_bins[i])


def get_dep(blocks, blocks_o, now, s, e, dep):
	if dep == 0:
		return min(10, blocks[now][0])
	if dep == 1:
		return get_avg_pre_coef(blocks[now], s)
	if dep == 2:
		return get_avg_pre_coef(get_previous_block(blocks, now), s)
	if dep == 3:
		t = 0
		b_pre = get_previous_block(blocks, now)
		for i in range(s, min(s+6, 63) + 1):
			if b_pre[i]:
				return b_pre[i]
		return 0
		
		
		t = 0
		if blocks[now][0] > 5:
			return 11
		b_pre = get_previous_block(blocks, now)
		for i in range(s, min(s+6, 63) + 1):
			if b_pre[i]:
				return b_pre[i]
		return 0
		
		ss = max(s - 2, 1)
		ee = min(s + 2, 63)
		t = 0.0
		for i in range(ss, ee+1):
			t += b_pre[i]*1.0/avg_coef[i]
		return int(t/(ee + 1 - ss)*10)
		#return b_pre[s]
	if dep == 4:
		b = blocks[now]
		return b[s-1]
		i = 63
		while i > 0:
			if b_pre[i]:
				break
			i -= 1
		if i >= 40:
			return 10
		else:
			return i/4
	if dep == 5:
		su = 0
		ma = 0
		sign = 0
		n = 0
		pos = -1
		for x in range(now - 1, max(0, now - 6), -1):
			if blocks[x+1][0] > 5:
				break
			for xx in range(s, min(64, s+5)):
				ma += avg_coef[xx]
				if blocks[x][xx]:
					if pos == -1:
						pos = xx
					else:
						if xx == pos:
							sign += blocks_o[x][xx]
							n += 1
					su += blocks[x][xx]
					break

#		if not ma:
#			return 21
		if not ma:
			return len(apc_bins[1]) + blocks[now][0] - 5
		return scale(su*1.0/ma, s)
		#return te
		bit = 0
		if n:
			bit = lib.get_bits(sign/n)
		if bit >= 1:
			if sign > 0:
				return te + 10
			else:
				return te + 20
		else:
			return te

def record_code(b, b_o, now, c, start, end, oc):
	global dep1, dep2
	d1 = get_dep(b, b_o, now, start, end, dep1)
	d2 = get_dep(b, b_o, now, start, end, dep2)
	oc[start][d1][d2][c] += 1
	
def record_jpeg(b, b_o, now, c, start, end, oc):
	global dep1, dep2, code
	d1 = get_dep(b, b_o, now, start, end, dep1)
	d2 = get_dep(b, b_o, now, start, end, dep2)
	oc[start][d1][d2] += code[abs(c)]	

def parse_dep(s):
	global apc_bins
	if s == "0": 
		return 0, 10
	elif s == "1": #avg_pre_coef
		return 1, len(apc_bins[1]) + 1
	elif s == "2": #avg_pre_block_coef
		return 2, len(apc_bins[1]) + 1
	elif s == "3": #pre_block_coef
		return 3, 11
	elif s == "4":
		return 4, 10
	elif s == "5":
		return 5, len(apc_bins[1]) + 6

def save_code_table(c, oc, i, d1, d2, table_folder, index_file):
	o = 0
	for x in oc:
		o += oc[x]
	
	if not o:
		return
	index_file.write(str(i) + "\t" + str(d1) + "\t" + str(d2) + ":\t" + str(o) + "\n")
	
	f = open(table_folder + "/" + str(i)+"_"+str(d1)+"_"+str(d2)+".table", "w")
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
	
def fprint(string):
	global index_file
	index_file.write(string + "\n")
	
def get_previous_block(b, n):
	if n==0:
		return [0]*64
	else:
		return b[n-1]
		

def get_optimized_bits(f):
	total_bits = 0
	for c in range(3):
		comp = str(c)	
		if comp == "0":
			code = lib.get_luminance_codes()
		else:
			code = lib.get_chrominance_codes()
			
		block = lib.get_blocks_all_in_bits(f, comp)

		l_total_bits = 0
		l_run_length_bits = 0
		l_dc_s = 0
		l_dc_b = 0
		l_ac_b = 0

		co = {}
		oc = {}

		for b in range(1, AC_BITS + 1):
			oc[(z<<4) + b] = 0			# for one run-length, positive sign
		oc[0] = 0	# 0 for EOB
		oc[0xf0] = 0

		oc_dc = {}
		co_dc = {}
		
		for ii in range(len(block)):
			x, dc_s_bits, dc_bits, r, coef_bits = lib.get_bits_detail(block[ii], code, comp=="0")
			l_ac_b += coef_bits
			l_run_length_bits += r
			l_dc_s += dc_s_bits
			l_dc_b += dc_bits
			l_total_bits += x		

			# for dc symbol:
			b = block[ii]
			oc_dc[b[0]] += 1
			r = 0
			pos = 1
			for i in range(1, 64):
				if b[i] == 0:
					r += 1
					continue

				while (r > 15):
					oc[0xf0] += 1
					pos += 16
					r -= 16

				oc[(r << 4) + b[i]] += 1
				pos = i + 1
				r = 0
			if r > 0:
				oc[0] += 1

		if l_dc_s + l_dc_b + l_run_length_bits + l_ac_b != l_total_bits:
			fprint("train set not equal")
		fprint("TRAIN SET:\tdc symbol length:" + str(l_dc_s) + "\tdc actual bits:" + str(l_dc_b) + "\trun length bits:" + str(l_run_length_bits) + "\tactual AC bits:" + str(l_ac_b) + "\ttotal bits:" + str(l_total_bits))
		

		co_dc = lib.huff_encode(oc_dc, lib.bits_dc_luminance)
		co = lib.huff_encode(oc, code)
		
		
