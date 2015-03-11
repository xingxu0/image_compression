import math, copy, glob, os, sys, pickle
from heapq import heappush, heappop, heapify
from collections import defaultdict
from copy import *

INT_MAX = 65535

bits_ac_luminance = [0, 0, 2, 1, 3, 3, 2, 4, 3, 5, 5, 4, 4, 0, 0, 1, 0x7d]
val_ac_luminance = [ 0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12,
      0x21, 0x31, 0x41, 0x06, 0x13, 0x51, 0x61, 0x07,
      0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xa1, 0x08,
      0x23, 0x42, 0xb1, 0xc1, 0x15, 0x52, 0xd1, 0xf0,
      0x24, 0x33, 0x62, 0x72, 0x82, 0x09, 0x0a, 0x16,
      0x17, 0x18, 0x19, 0x1a, 0x25, 0x26, 0x27, 0x28,
      0x29, 0x2a, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39,
      0x3a, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49,
      0x4a, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59,
      0x5a, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69,
      0x6a, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79,
      0x7a, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89,
      0x8a, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98,
      0x99, 0x9a, 0xa2, 0xa3, 0xa4, 0xa5, 0xa6, 0xa7,
      0xa8, 0xa9, 0xaa, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6,
      0xb7, 0xb8, 0xb9, 0xba, 0xc2, 0xc3, 0xc4, 0xc5,
      0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xd2, 0xd3, 0xd4,
      0xd5, 0xd6, 0xd7, 0xd8, 0xd9, 0xda, 0xe1, 0xe2,
      0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9, 0xea,
      0xf1, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7, 0xf8,
      0xf9, 0xfa ]

bits_ac_chrominance = [ 0, 0, 2, 1, 2, 4, 4, 3, 4, 7, 5, 4, 4, 0, 1, 2, 0x77]
val_ac_chrominance = [ 0x00, 0x01, 0x02, 0x03, 0x11, 0x04, 0x05, 0x21,
      0x31, 0x06, 0x12, 0x41, 0x51, 0x07, 0x61, 0x71,
      0x13, 0x22, 0x32, 0x81, 0x08, 0x14, 0x42, 0x91,
      0xa1, 0xb1, 0xc1, 0x09, 0x23, 0x33, 0x52, 0xf0,
      0x15, 0x62, 0x72, 0xd1, 0x0a, 0x16, 0x24, 0x34,
      0xe1, 0x25, 0xf1, 0x17, 0x18, 0x19, 0x1a, 0x26,
      0x27, 0x28, 0x29, 0x2a, 0x35, 0x36, 0x37, 0x38,
      0x39, 0x3a, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48,
      0x49, 0x4a, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58,
      0x59, 0x5a, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68,
      0x69, 0x6a, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78,
      0x79, 0x7a, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87,
      0x88, 0x89, 0x8a, 0x92, 0x93, 0x94, 0x95, 0x96,
      0x97, 0x98, 0x99, 0x9a, 0xa2, 0xa3, 0xa4, 0xa5,
      0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xb2, 0xb3, 0xb4,
      0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xc2, 0xc3,
      0xc4, 0xc5, 0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xd2,
      0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8, 0xd9, 0xda,
      0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8, 0xe9,
      0xea, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7, 0xf8,
      0xf9, 0xfa ]
      
bits_dc_luminance = [2,3,3,3,3,3,4,5,6,7,8,9]
bits_dc_chrominance = [2,2,2,3,4,5,6,7,8,9,10,11]

avg_actual_coef_600_0 = {0 : 251 , 1 : 150 , 2 : 147 , 3 : 85 , 4 : 94 , 5 : 136 , 6 : 67 , 7 : 58 , 8 : 61 , 9 : 63 , 10 : 45 , 11 : 41 , 12 : 42 , 13 : 31 , 14 : 36 , 15 : 16 , 16 : 25 , 17 : 24 , 18 : 24 , 19 : 23 , 20 : 24 , 21 : 11 , 22 : 10 , 23 : 12 , 24 : 17 , 25 : 12 , 26 : 7 , 27 : 10 , 28 : 10 , 29 : 5 , 30 : 7 , 31 : 8 , 32 : 8 , 33 : 7 , 34 : 5 , 35 : 8 , 36 : 4 , 37 : 4 , 38 : 5 , 39 : 6 , 40 : 5 , 41 : 4 , 42 : 6 , 43 : 8 , 44 : 4 , 45 : 3 , 46 : 3 , 47 : 4 , 48 : 3 , 49 : 3 , 50 : 2 , 51 : 2 , 52 : 2 , 53 : 6 , 54 : 3 , 55 : 1 , 56 : 2 , 57 : 3 , 58 : 2 , 59 : 1 , 60 : 2 , 61 : 2 , 62 : 2 , 63 : 2}

avg_actual_coef_600_1 = {1 : 40 , 2 : 42 , 3 : 23 , 4 : 20 , 5 : 20 , 6 : 6 , 7 : 11 , 8 : 13 , 9 : 8 , 10 : 2 , 11 : 3 , 12 : 5 , 13 : 4 , 14 : 3 , 15 : 2 , 16 : 2 , 17 : 2 , 18 : 2 , 19 : 2 , 20 : 2 , 21 : 1 , 22 : 1 , 23 : 1 , 24 : 1 , 25 : 2 , 26 : 1 , 27 : 1 , 28 : 1 , 29 : 1 , 30 : 1 , 31 : 1 , 32 : 1 , 33 : 1 , 34 : 1 , 35 : 1 , 36 : 1 , 37 : 1 , 38 : 1 , 39 : 1 , 40 : 1 , 41 : 1 , 42 : 1 , 43 : 1 , 44 : 1 , 45 : 1 , 46 : 1 , 47 : 1 , 48 : 1 , 49 : 1 , 50 : 1 , 51 : 1 , 52 : 1 , 53 : 1 , 54 : 1 , 55 : 1 , 56 : 1 , 57 : 1 , 58 : 1 , 59 : 0 , 60 : 1 , 61 : 0 , 62 : 1 , 63 : 1}

avg_coef_600_0 = {1 : 8 , 2 : 8 , 3 : 7 , 4 : 7 , 5 : 8 , 6 : 7 , 7 : 6 , 8 : 6 , 9 : 6 , 10 : 6 , 11 : 6 , 12 : 6 , 13 : 5 , 14 : 6 , 15 : 5 , 16 : 5 , 17 : 5 , 18 : 5 , 19 : 5 , 20 : 5 , 21 : 4 , 22 : 4 , 23 : 4 , 24 : 5 , 25 : 4 , 26 : 4 , 27 : 4 , 28 : 4 , 29 : 3 , 30 : 3 , 31 : 4 , 32 : 4 , 33 : 3 , 34 : 3 , 35 : 4 , 36 : 3 , 37 : 3 , 38 : 3 , 39 : 3 , 40 : 3 , 41 : 3 , 42 : 3 , 43 : 4 , 44 : 3 , 45 : 3 , 46 : 3 , 47 : 3 , 48 : 3 , 49 : 3 , 50 : 3 , 51 : 3 , 52 : 3 , 53 : 3 , 54 : 2 , 55 : 2 , 56 : 2 , 57 : 2 , 58 : 2 , 59 : 2 , 60 : 2 , 61 : 2 , 62 : 2 , 63 : 2}

avg_coef_600_1 = {1 : 6 , 2 : 6 , 3 : 5 , 4 : 5 , 5 : 5 , 6 : 4 , 7 : 4 , 8 : 4 , 9 : 4 , 10 : 3 , 11 : 3 , 12 : 3 , 13 : 3 , 14 : 2 , 15 : 2 , 16 : 2 , 17 : 2 , 18 : 2 , 19 : 2 , 20 : 2 , 21 : 1 , 22 : 1 , 23 : 1 , 24 : 1 , 25 : 2 , 26 : 1 , 27 : 1 , 28 : 1 , 29 : 1 , 30 : 1 , 31 : 1 , 32 : 1 , 33 : 1 , 34 : 1 , 35 : 1 , 36 : 1 , 37 : 1 , 38 : 1 , 39 : 1 , 40 : 1 , 41 : 1 , 42 : 1 , 43 : 1 , 44 : 1 , 45 : 1 , 46 : 1 , 47 : 1 , 48 : 1 , 49 : 1 , 50 : 1 , 51 : 1 , 52 : 1 , 53 : 1 , 54 : 1 , 55 : 1 , 56 : 1 , 57 : 1 , 58 : 1 , 59 : 1 , 60 : 1 , 61 : 1 , 62 : 1 , 63 : 1}

avg_coef_1200_0 = {1 : 8 , 2 : 8 , 3 : 7 , 4 : 8 , 5 : 8 , 6 : 7 , 7 : 6 , 8 : 7 , 9 : 7 , 10 : 6 , 11 : 6 , 12 : 6 , 13 : 6 , 14 : 6 , 15 : 5 , 16 : 5 , 17 : 5 , 18 : 5 , 19 : 5 , 20 : 6 , 21 : 4 , 22 : 4 , 23 : 4 , 24 : 4 , 25 : 5 , 26 : 4 , 27 : 4 , 28 : 4 , 29 : 3 , 30 : 3 , 31 : 3 , 32 : 3 , 33 : 4 , 34 : 3 , 35 : 3 , 36 : 3 , 37 : 3 , 38 : 3 , 39 : 3 , 40 : 3 , 41 : 3 , 42 : 3 , 43 : 3 , 44 : 3 , 45 : 2 , 46 : 2 , 47 : 2 , 48 : 2 , 49 : 2 , 50 : 2 , 51 : 2 , 52 : 2 , 53 : 2 , 54 : 2 , 55 : 2 , 56 : 2 , 57 : 2 , 58 : 2 , 59 : 2 , 60 : 2 , 61 : 1 , 62 : 1 , 63 : 1}

avg_coef_1200_1 = {1 : 6 , 2 : 6 , 3 : 5 , 4 : 5 , 5 : 5 , 6 : 4 , 7 : 4 , 8 : 4 , 9 : 3 , 10 : 3 , 11 : 3 , 12 : 3 , 13 : 2 , 14 : 2 , 15 : 2 , 16 : 2 , 17 : 2 , 18 : 2 , 19 : 2 , 20 : 2 , 21 : 1 , 22 : 1 , 23 : 2 , 24 : 1 , 25 : 1 , 26 : 1 , 27 : 1 , 28 : 1 , 29 : 1 , 30 : 1 , 31 : 1 , 32 : 1 , 33 : 1 , 34 : 1 , 35 : 1 , 36 : 1 , 37 : 1 , 38 : 1 , 39 : 1 , 40 : 1 , 41 : 1 , 42 : 1 , 43 : 1 , 44 : 1 , 45 : 1 , 46 : 1 , 47 : 1 , 48 : 1 , 49 : 1 , 50 : 1 , 51 : 1 , 52 : 1 , 53 : 1 , 54 : 1 , 55 : 1 , 56 : 1 , 57 : 1 , 58 : 1 , 59 : 1 , 60 : 1 , 61 : 1 , 62 : 1 , 63 : 1}

def generate_bits(vals, bits):
	ret = {}
	now = 0
	for b in range(len(bits)):
		t = bits[b]
		for i in range(t):
			ret[vals[now]] = b
			now += 1
	for x in range(255):
		if x in ret:
			print ret[x],",",
		else:
			print -1,",",
	return ret	

def get_luminance_codes():
	return generate_bits(val_ac_luminance, bits_ac_luminance)

def get_chrominance_codes():
	return generate_bits(val_ac_chrominance, bits_ac_chrominance)

def get_jpeg_bits_with_dc(coefs, st, en, code, last_dc, luminance):
	dc_bits = get_bits(abs(coefs[0]-last_dc))
	if luminance:
		dc_s_bits = bits_dc_luminance[dc_bits]
	else:
		dc_s_bits = bits_dc_chrominance[dc_bits]
	return dc_bits + dc_s_bits + get_jpeg_bits(coefs, st + 1, en, code, False)[0], coefs[0]
	
def get_jpeg_bits_with_dc_detail(coefs, st, en, code, last_dc, luminance):
	dc_bits = get_bits(abs(coefs[0]-last_dc))
	if luminance:
		dc_s_bits = bits_dc_luminance[dc_bits]
	else:
		dc_s_bits = bits_dc_chrominance[dc_bits]
	ret = get_jpeg_bits(coefs, st + 1, en, code, False)
	return dc_bits + dc_s_bits + ret[0], coefs[0], dc_s_bits, dc_bits, ret[0] - ret[1], ret[1]
	
def get_jpeg_bits_detail(coefs, st, en, code, luminance):
	dc_bits = coefs[0]
	if luminance:
		dc_s_bits = bits_dc_luminance[dc_bits]
	else:
		dc_s_bits = bits_dc_chrominance[dc_bits]
	ret = get_jpeg_bits(coefs, st + 1, en, code, False)
	return dc_bits + dc_s_bits + ret[0], dc_s_bits, dc_bits, ret[0] - ret[1], ret[1]

def get_jpeg_bits_detail_all_positive(coefs, st, en, code, luminance):
	dc_bits = coefs[0]
	if luminance:
		dc_s_bits = bits_dc_luminance[dc_bits]
	else:
		dc_s_bits = bits_dc_chrominance[dc_bits]
	ret = get_jpeg_bits_all_positive(coefs, st + 1, en, code, False)
	return dc_bits + dc_s_bits + ret[0], dc_s_bits, dc_bits, ret[0] - ret[1], ret[1], ret[2]


def print_prefix(pre_n, pre):
	for i in range(pre_n):
		print pre[i],

def print_prefix_to_file(pre_n, pre, f):
	for i in range(pre_n-1):
		f.write(str(pre[i]) + " ")	
	f.write(str(pre[pre_n-1]))

#get total bits for one block
def get_total_bits(i, code, last_dc, comp):
	return get_jpeg_bits_with_dc(i, 0, len(i)-1, code, last_dc, comp)

def get_total_bits_detail(i, code, last_dc, comp):
	return get_jpeg_bits_with_dc_detail(i, 0, len(i)-1, code, last_dc, comp)
	
def get_bits_detail(i, code, comp):
	return get_jpeg_bits_detail(i, 0, len(i)-1, code, comp)

def get_bits_detail_all_positive(i, code, comp):
	return get_jpeg_bits_detail_all_positive(i, 0, len(i)-1, code, comp)


#get run-length bits only for one block (does not include DC bits, and actual coefficient)
def get_run_length_bits(i, code):
	return get_jpeg_bits(i, 1, len(i)-1, code, True)[0]

def get_run_length_bits_detail(i, code):
	return get_jpeg_bits(i, 1, len(i)-1, code, True)

# if COEFS is ended with a -1, that means the prefix is all 0 afterwards till the end of block, it also means n is 63
def get_jpeg_bits(coefs, st, en, code, run_length_only):
	b = 0
	r = 0
	coef_bits = 0
	for i in range(st, en + 1):
		if coefs[i] == 0:
			r += 1
			continue
	
		while (r > 15):
			b += code[0xf0]
			r -= 16
	
		b += code[(r << 4) + coefs[i]]
		if not run_length_only:
			b += coefs[i]
			coef_bits += coefs[i]
		r = 0
	if (st == 1):
		if (en == 63 and r > 0):
			b += code[0]
	else:
		if (en == 62 and r > 0):
			b += code[0]
#	print_prefix(en + 1, coefs)
#	print b
	return b, coef_bits

def get_jpeg_bits_all_positive(coefs, st, en, code, run_length_only):
	b = 0
	r = 0
	coef_bits = 0
	saving = 0
	for i in range(st, en + 1):
		if coefs[i] == 0:
			r += 1
			continue
	
		while (r > 15):
			b += code[0xf0]
			r -= 16
	
		b += code[(r << 4) + coefs[i]]
		if not run_length_only:
			b += coefs[i]-1
			coef_bits += coefs[i]-1
			saving +=1
		r = 0
	if (st == 1):
		if (en == 63 and r > 0):
			b += code[0]
	else:
		if (en == 62 and r > 0):
			b += code[0]
#	print_prefix(en + 1, coefs)
#	print b
	return b, coef_bits, saving
	

def get_blocks(filename, comp):
	ff = filename.split("|")
	blocks = []
	for f in ff:
		t_blocks = open(f).readlines()
		last_dc = 0
		for i in range(len(t_blocks)):
			s = t_blocks[i][:-2].split(" ")
			ii = []
			if s[0] == comp + ":":
				for j in range(1, len(s)):
					ii.append(int(s[j]))
				blocks.append(ii)
	return blocks
	
def get_blocks_with_dc_in_diff(filename, comp):   # the first DC coef will be the difference
	ff = filename.split("|")
	blocks = []
	for f in ff:
		t_blocks = open(f).readlines()
		last_dc = 0
		for i in range(len(t_blocks)):
			s = t_blocks[i][:-2].split(" ")
			ii = []
			if s[0] == comp + ":":
				for j in range(1, len(s)):
					if j==1:
						ii.append(int(s[j]) - last_dc)
						last_dc = int(s[j])
					else:
						ii.append(int(s[j]))
				blocks.append(ii)
	return blocks

def get_blocks_with_dc_in_diff_with_threshold(filename, comp):   # the first DC coef will be the difference
	ff = filename.split("|")
	blocks = []
	for f in ff:
		t_blocks = open(f).readlines()
		last_dc = 0
		last_dc_t = 0
		for i in range(len(t_blocks)):
			s = t_blocks[i][:-2].split(" ")
			ii = []
			if s[0] == comp + ":":
				for j in range(1, len(s)):
					if j==1:
						ii.append(get_bits(abs((int(s[j]) >> 1) - last_dc)))
						print get_bits(abs((int(s[j]) >> 1) - last_dc)), get_bits(abs(int(s[j]) - last_dc_t))
						last_dc = (int(s[j]) >> 1)
						last_dc_t = int(s[j])
					else:
						ii.append(int(s[j]))
				blocks.append(ii)
	return blocks
	

def get_bits(i_num):
	num = abs(i_num)
	if num == 0:
		return 0
	bits = 1
	while (num>>1):
		bits += 1
		num >>= 1
	return bits

def get_blocks_with_bits(filename, comp):		# the first DC coef will be actual value (not difference)
	ff = filename.split("|")
	blocks = []
	for f in ff:
		t_blocks = open(f).readlines()
		for i in range(len(t_blocks)):
			s = t_blocks[i][:-2].split(" ")
			ii = []
			if s[0] == comp + ":":
				for j in range(1, len(s)):
					if j==1:
						ii.append(int(s[j]))
					else:
						ii.append(get_bits(abs(int(s[j]))))
				blocks.append(ii)
	return blocks
	
def get_blocks_all_in_bits(filename, comp):   # the first DC coef will be the bits of the difference, not actual value
	ff = filename.split("|")
	blocks = []
	for f in ff:
		t_blocks = open(f).readlines()
		last_dc = 0
		for i in range(len(t_blocks)):
			s = t_blocks[i][:-2].split(" ")
			ii = []
			if s[0] == comp + ":":
				for j in range(1, len(s)):
					if j==1:
						ii.append(get_bits(abs(int(s[j]) - last_dc)))
						last_dc = int(s[j])
					else:
						ii.append(get_bits(abs(int(s[j]))))
				blocks.append(ii)
	return blocks
	
def get_blocks_difference_all_in_bits(filename, comp):   # same to above function, but for AC it will calculate the bits of the difference
	ff = filename.split("|")
	blocks = []
	for f in ff:
		t_blocks = open(f).readlines()
		last_dc = 0
		last_block = [0]*65
		for i in range(len(t_blocks)):
			s = t_blocks[i][:-2].split(" ")
			ii = []
			if s[0] == comp + ":":
				for j in range(1, len(s)):
					if j==1:
						ii.append(get_bits(abs(int(s[j]) - last_dc)))
						last_dc = int(s[j])
					else:
						if int(last_block[j]) != int(s[j]) and int(last_block[j])*int(s[j])>0:#abs(int(last_block[j])) > 3:						
							print int(last_block[j]), int(s[j]), abs(int(s[j]) - int(last_block[j]))
							ii.append(get_bits(abs(int(s[j]) - int(last_block[j]))))
						else:
							ii.append(get_bits(abs(int(s[j]))))
				last_block = s
				blocks.append(ii)
	return blocks	
	
def get_entropy(prob):
	if prob == 0:
		return INT_MAX
	return int(math.ceil(-math.log(prob, 2)))
	
def get_predicted_run(b, b_pre, start, end):
	intra_block = 0
	for i in range(start):
		if b[i] == 0:
			intra_block += 1
	intra_block = min(16, intra_block)

	return min(intra_block, 10)

def get_predicted_size(b, b_pre, start, end):
	intra_block = 0
	t = 0
	c = 0
	if start == 1:
		intra_block = min(10, b[0])
	else:
		for i in range(1, start):
			if b[i]:
				t += b[i]
				c += 1
		if c:
			intra_block = t*1.0/c

	return int(intra_block)
	
def get_dependant_value(b, i):
	if i==1:
		return b[0]
	t = 0
	for x in range(1, i):
		t += b[x]
	return int(t*(0.3*(i/10)+1)/(i - 1))
	
def huff_encode(symb2freq, jpeg_code):
	# give 0 occurence value a reasonable probability, right now proportional to JPEG default table
	t = 0
	for x in symb2freq:
		t += symb2freq[x]
		
	# no data to infer huffman table, using default
	if not t:
		return deepcopy(jpeg_code)
	
	#Huffman encode the given dict mapping symbols to weights
	heap = [[wt, [sym, ""]] for sym, wt in symb2freq.items()]
	heapify(heap)
	while len(heap) > 1:
		lo = heappop(heap)
		hi = heappop(heap)
		for pair in lo[1:]:
			pair[1] = '0' + pair[1]
		for pair in hi[1:]:
			pair[1] = '1' + pair[1]
		heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

	temp = sorted(heappop(heap)[1:], key=lambda p: (len(p[-1]), p))
	ret = {}
	for p in temp:
		ret[p[0]] = len(p[1])
	return ret

def huff_encode_entropy_plus_extra(symb2freq, jpeg_code):
	t = 0
	for x in symb2freq:
		t += symb2freq[x]
		
	# no data to infer huffman table, using default
	if not t:
		return deepcopy(jpeg_code)

	extra_t = t*0.01
	for x in symb2freq:
		if not symb2freq[x]:
			symb2freq[x] = extra_t * math.sqrt(pow(2, - jpeg_code[x]))
		
	ret = {}
	for x in symb2freq:
		ret[x] = -math.log(symb2freq[x]*1.0/t, 2)
	return ret

def huff_encode_entropy(symb2freq, jpeg_code):
	t = 0
	for x in symb2freq:
		t += symb2freq[x]
		
	# no data to infer huffman table, using default
	if not t:
		return deepcopy(jpeg_code)
		
	ret = {}
	for x in symb2freq:
		ret[x] = -math.log(symb2freq[x]*1.0/t, 2)
	return ret

def huff_encode_plus_extra(symb2freq, jpeg_code):
	# give 0 occurence value a reasonable probability, right now proportional to JPEG default table
	t = 0
	for x in symb2freq:
		t += symb2freq[x]
		
	# no data to infer huffman table, using default
	if not t:
		return deepcopy(jpeg_code)
	
	extra_t = t*0.01
	for x in symb2freq:
		if not symb2freq[x]:
			symb2freq[x] = extra_t * math.sqrt(pow(math.e, - jpeg_code[x]))
			
	#Huffman encode the given dict mapping symbols to weights
	heap = [[wt, [sym, ""]] for sym, wt in symb2freq.items()]
	heapify(heap)
	while len(heap) > 1:
		lo = heappop(heap)
		hi = heappop(heap)
		for pair in lo[1:]:
			pair[1] = '0' + pair[1]
		for pair in hi[1:]:
			pair[1] = '1' + pair[1]
		heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

	temp = sorted(heappop(heap)[1:], key=lambda p: (len(p[-1]), p))
	ret = {}
	for p in temp:
		ret[p[0]] = len(p[1])
	return ret

def huff_encode_plus_extra_better_DC(symb2freq, jpeg_code):
	# give 0 occurence value a reasonable probability, right now proportional to JPEG default table
	t = 0
	for x in symb2freq:
		t += symb2freq[x]
		
	# no data to infer huffman table, using default
	if not t:
		return deepcopy(jpeg_code)
	
	zero = 0
	for x in symb2freq:
		if symb2freq[x] == 0:
			zero += 1
	extra_t = t*0.01
	for x in symb2freq:
		if not symb2freq[x]:
			symb2freq[x] = extra_t*1.0/zero
			
	#Huffman encode the given dict mapping symbols to weights
	heap = [[wt, [sym, ""]] for sym, wt in symb2freq.items()]
	heapify(heap)
	while len(heap) > 1:
		lo = heappop(heap)
		hi = heappop(heap)
		for pair in lo[1:]:
			pair[1] = '0' + pair[1]
		for pair in hi[1:]:
			pair[1] = '1' + pair[1]
		heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

	temp = sorted(heappop(heap)[1:], key=lambda p: (len(p[-1]), p))
	ret = {}
	for p in temp:
		ret[p[0]] = len(p[1])
		if (ret[p[0]] > 32):
			print "!"
	return ret

def huff_encode_plus_extra_ac_sign(symb2freq, jpeg_code):
	# give 0 occurence value a reasonable probability, right now proportional to JPEG default table
	t = 0
	for x in symb2freq:
		t += symb2freq[x]
		
	# no data to infer huffman table, using default
	if not t:
		ret = deepcopy(jpeg_code)
		for x in jpeg_code:
			ret[(1<<8)+x] = jpeg_code[x]
		return ret
	
	zero = 0
	for x in symb2freq:
		if symb2freq[x] == 0:
			zero += 1
	extra_t = t*0.01
	extra_t = 0
	for x in symb2freq:
		if not symb2freq[x]:
			symb2freq[x] = extra_t*1.0/zero
			
	#Huffman encode the given dict mapping symbols to weights
	heap = [[wt, [sym, ""]] for sym, wt in symb2freq.items()]
	heapify(heap)
	while len(heap) > 1:
		lo = heappop(heap)
		hi = heappop(heap)
		for pair in lo[1:]:
			pair[1] = '0' + pair[1]
		for pair in hi[1:]:
			pair[1] = '1' + pair[1]
		heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

	temp = sorted(heappop(heap)[1:], key=lambda p: (len(p[-1]), p))
	ret = {}
	for p in temp:
		ret[p[0]] = len(p[1])
	return ret

def huff_encode_plus_extra_all(symb2freq, jpeg_code):
	# give 0 occurence value a reasonable probability, right now proportional to JPEG default table
	t = 0
	for x in symb2freq:
		t += symb2freq[x]
		
	# no data to infer huffman table, using default
	if not t:
		ret = deepcopy(jpeg_code)
		for x in jpeg_code:
			ret[(1<<8)+x] = jpeg_code[x]
		return ret, 0
	
	zero = 0
	for x in symb2freq:
		if symb2freq[x] == 0:
			zero += 1
	extra_t = t*0.01
	for x in symb2freq:
		if not symb2freq[x]:
			symb2freq[x] = extra_t*1.0/zero
			
	#Huffman encode the given dict mapping symbols to weights
	heap = [[wt, [sym, ""]] for sym, wt in symb2freq.items()]
	heapify(heap)
	while len(heap) > 1:
		lo = heappop(heap)
		hi = heappop(heap)
		for pair in lo[1:]:
			pair[1] = '0' + pair[1]
		for pair in hi[1:]:
			pair[1] = '1' + pair[1]
		heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

	temp = sorted(heappop(heap)[1:], key=lambda p: (len(p[-1]), p))
	ret = {}
	max_len = -1
	for p in temp:
		ret[p[0]] = len(p[1])
		if (ret[p[0]] > 32):
			print "!", ret[p[0]]
		if ret[p[0]]>max_len:
			max_len = ret[p[0]]
	return ret, max_len


def huff_encode_plus_extra_handle_2_separately(symb2freq, jpeg_code):
	# give 0 occurence value a reasonable probability, right now proportional to JPEG default table
	t = 0
	for x in symb2freq:
		t += symb2freq[x]
		
	# no data to infer huffman table, using default
	if not t:
		return deepcopy(jpeg_code)
	
	extra_t = t*0.01
	zero = 0
	for x in symb2freq:
		if symb2freq[x] == 0:
			zero += 1

	for x in symb2freq:
		if not symb2freq[x]:
			symb2freq[x] = extra_t *1.0/zero
			
	#Huffman encode the given dict mapping symbols to weights
	heap = [[wt, [sym, ""]] for sym, wt in symb2freq.items()]
	heapify(heap)
	while len(heap) > 1:
		lo = heappop(heap)
		hi = heappop(heap)
		for pair in lo[1:]:
			pair[1] = '0' + pair[1]
		for pair in hi[1:]:
			pair[1] = '1' + pair[1]
		heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

	temp = sorted(heappop(heap)[1:], key=lambda p: (len(p[-1]), p))
	ret = {}
	for p in temp:
		ret[p[0]] = len(p[1])
	return ret

    
def get_predicted_SIZE1(b, b_pre, start, end):
	global weight1
	intra_block = 0
	for i in range(start):
		if b[i] == 0:
			intra_block += 1
	intra_block = min(16, intra_block)
	
	inter_block = 0
	for i in range(start, 64):
		if b_pre[i]:
			break
		else:
			inter_block += 1
			if inter_block == 16:
				break
	#weight = 0 #0.7 + b[0]*0.3/11    # adjust weight on these two blocks' difference				
	#inter_block = int(inter_block*1.0/(64 - start)*16)
	return min(int(weight1*inter_block + (1-weight1)*intra_block), 10)

def get_predicted_size(b, b_pre, start, end):
	global weight2
	intra_block = 0
	t = 0
	c = 0
	if start == 1:
		intra_block = min(10, b[0])
	else:
		for i in range(1, start):
			if b[i]:
				t += b[i]
				c += 1
		if c:
			intra_block = t*1.0/c

	inter_block = 0
	for i in range(start, 64):
		if b_pre[i]:
			inter_block = b_pre[i]
			break
	#weight = 0 #0.7 + b[0]*0.3/11    # adjust weight on these two blocks' difference
	return int(weight2*inter_block + (1-weight2)*intra_block)    
	
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
	global avg_coef
	if i==1:
		return min(10, b[0])*1.0/11
	t = 0
	ma = 1 
	#for x in range(1, i):
	for x in range(1, i):
		t += b[x]
		ma += avg_coef[x]
	return t*1.0/ma

def get_avg_pre_actual_coef(b, b_o, i):
	global avg_coef, avg_actual_coef
	if i==1:
		#return min(10, b[0])
		return scale_actual_coef(abs(b_o[0]*1.0/avg_actual_coef[0]), i)
	t = 0
	ma = 0
	for x in range(1, i):
		t += abs(b_o[x])
		ma += avg_actual_coef[x]
	return scale_actual_coef(t*1.0/ma, i)
	
	
def scale(f, i, one_or_two):
	global apc_bins, papc_bins
	bins = 0
	if one_or_two == "1":
		bins = apc_bins
	else:
		bins = papc_bins
	for x in range(len(bins[i])):
		if f < bins[i][x]:
			return x
	return len(bins[i])

def scale_block(f, i):
	global papc_bins, avg_coef_max
	for x in range(len(papc_bins[i])):
		#if f < (apc_bins[j+1][x]*avg_coef_max[j+1] - apc_bins[i][x]*avg_coef_max[i])*1.0/(avg_coef_max[j+1] - avg_coef_max[i]):
		if f < papc_bins[i][x]:
			return x
	return len(papc_bins[i])
	
def scale_actual_coef(f, i):
	global aapc_bins
	for x in range(len(aapc_bins[i])):
		if f < aapc_bins[i][x]:
			return x
	return len(aapc_bins[i])	


def get_dep(blocks, blocks_o, now, s, e, dep, one_or_two, b_mcu1, b_mcu2):
	global apc_bins, avg_coef,look_forward_coef, look_backward_block
	if dep == 0:
		return min(10, blocks[now][0])
	if dep == 1:
		v = get_avg_pre_coef(blocks[now], s)
		return scale(v, s, one_or_two)
	if dep == 2:
		v = get_avg_pre_coef(get_previous_block(blocks, now), s)
		return scale(v, s, one_or_two)
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
		for x in range(now - 1, max(0, now - 3), -1):
			if blocks[x+1][0] > 5:
				break
			for xx in range(s, min(64, s+5)):
				ma += avg_coef[xx]
				if blocks[x][xx]:
					su += blocks[x][xx]
					#break

#		if not ma:
#			return 21
		if not ma:
			if blocks[now][0] > 11:
				print "DC out of range", blocks[now]
			return len(papc_bins[1]) + blocks[now][0] - 5
		return scale_block(su*1.0/ma, s)
	if dep == 6:
		su = 0
		ma = 0
		sign = 0
		n = 0
		pos = -1
		for x in range(now - 1, max(0, now - 2), -1):
			if blocks[x+1][0] > 2:
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
		if ma == 0:
			return get_dep(blocks, blocks_o, now, s, e, 3)
		return scale(su*1.0/ma, s) + 12
	
	if dep == 7:
		return get_avg_pre_actual_coef(blocks[now], blocks_o[now], s)
		
	if dep == 8:
		if s==1:
			return int(abs(blocks_o[now][0]*200.0/avg_actual_coef[0]))
		t = 0
		ma = 0
		for x in range(1, s):
			t += abs(blocks_o[now][x])
			ma += avg_actual_coef[x]
		return int(t*200.0/ma)
	if dep == 9:
		seen, ma, su = get_previous_blocks_coef(blocks, now, s, e)
		return scale(su*1.0/ma, s, one_or_two)
	if dep == 10:
		ma, su = get_energy_level(blocks, now, s, e)
		return scale(su*1.0/ma, s, one_or_two)
	if dep == 11:
		ma, su = get_mcu_energy_level(b_mcu1, b_mcu2, now, s, e)
		return scale(su*1.0/ma, s, one_or_two)
	if dep == 12:
		seen, ma, su = get_previous_blocks_coef(blocks, now, s, e)
		t = scale(su*1.0/ma, s, one_or_two)
		x = 2
		ss = 0
		l = 0
		if one_or_two == "1":
			l = len(apc_bins[1])
		else:
			l = len(papc_bins[1])
		first_jj = 0
		for ii in range(x):
			temp_b = get_previous_block(blocks_o, now-ii)
			for jj in range(s, min(64,s+look_forward_coef)):
				if temp_b[jj] < 0:
					first_jj = jj
					ss -= 1
					break
				if temp_b[jj] > 0:
					ss += 1
					first_jj = jj
					break
		if ss == -2:
			return t + 2*(l + 1)
		elif ss == +2:
			return t + (l + 1)
		else:
			return t
			
		
	if dep == -1:
		return 0
		
def get_energy_level(blocks, now, s, e):
	global apc_bins, avg_coef,look_forward_coef, look_backward_block
	su = 0
	ma = 0
	if s <= 1:
		for x in range(now - 1, max(0, now - look_backward_block) - 1, -1):
			for xx in range(s, min(64, s+look_forward_coef)):
				ma += avg_coef[xx]
				su += blocks[x][xx]
				if blocks[x][xx] >0:
					break
	else:
		for x in range(1, s):
			su += blocks[now][x]
			ma += avg_coef[x]
	if ma==0:
		ma = 1
	return ma, su	

def get_mcu_energy_level(b1, b2, now, s, e):
	global max_pos1, max_pos2
	su = 0
	ma = 0
	now_t = now / 4
	for x in range(1,10):
		su += b1[now_t][x]
		su += b2[now_t][x]
		ma += max_pos1[x]
		ma += max_pos2[x]
	return ma, su	
		
def get_previous_blocks_coef(blocks, now, s, e):
	global apc_bins, avg_coef,look_forward_coef, look_backward_block
	su = 0
	ma = look_backward_block
	sign = 0
	n = 0
	pos = -1
	#print "now:", now
	seen = True
	#for x in range(now - 1, now - look_backward_block - 1, -1):
	for x in range(now - 1, max(0, now - look_backward_block) - 1, -1):
		#if blocks[x+1][0] > 5:
		#	break	
		for xx in range(s, min(64, s+look_forward_coef)):
			ma += avg_coef[xx]
			#if x < 0:
			#	continue
			su += blocks[x][xx]
			if blocks[x][xx] >0:
				break
		
	if ma ==0:
		ma = 1
	return seen, ma, su

def get_previous_blocks_coef_for_DC(blocks, now):
	global apc_bins
	su = 0
	ma = 0
	sign = 0
	n = 0
	pos = -1
	#print "now:", now
	seen = True
	for x in range(now - 1, max(0, now - look_backward_block) - 1, -1):
		#if blocks[x+1][0] > 5:
		#	break	
		for xx in range(1, min(64, 1+look_forward_coef)):
			ma += avg_coef[xx]
			su += blocks[x][xx]
			if blocks[x][xx] >0:
				break
		
	if ma ==0:
		ma = 1
	f = su*1.0/ma
	bins = apc_bins
	for x in range(len(bins[1])):
		if f < bins[1][x]:
			return x
	return len(bins[1])
		
''' the other version		
def get_previous_blocks_coef(blocks, now, s, e):
	global apc_bins, avg_coef,look_forward_coef, look_backward_block
	su = 0
	ma = 0
	sign = 0
	n = 0
	pos = -1
	#print "now:", now
	seen = False 
	for x in range(now - 1, max(0, now - look_backward_block) - 1, -1):
		if blocks[x+1][0] > 5:
			break
		seen = True				
		for xx in range(s, min(64, s+look_forward_coef)):
			ma += avg_coef[xx]
			su += blocks[x][xx]
			#if blocks[x][xx] >0:
			#	break
	#if ma ==0:
	#	ma = 1
	return seen, ma, su
'''

def record_code(b, b_o, now, c, start, end, oc, b_mcu1, b_mcu2):
	global dep1, dep2, wrong_keys
	d1= get_dep(b, b_o, now, start, end, dep1, "1", b_mcu1, b_mcu2)
	d2= get_dep(b, b_o, now, start, end, dep2, "2", b_mcu1, b_mcu2)
	if d1<len(oc[start]) and d2<len(oc[start][d1]):
		oc[start][d1][d2][c] += 1
	else:
		print "*", d1, d2
		wrong_keys += 1
	return start, d1, d2, c

def record_jpeg(b, b_o, now, c, start, end, oc, b_mcu1, b_mcu2):
	global dep1, dep2, code, wrong_keys, wrong_desc, wrong_saw
	d1 = get_dep(b, b_o, now, start, end, dep1, "1", b_mcu1, b_mcu2)
	d2 = get_dep(b, b_o, now, start, end, dep2, "2", b_mcu1, b_mcu2)
	if d1<len(oc[start]) and d2<len(oc[start][d1]):
		oc[start][d1][d2] += code[abs(c)]
	else:
		wrong_keys += 1
		if not wrong_saw:
			wrong_desc = []
			wrong_desc.append(d1)
			wrong_desc.append(d2)
			for i in range(1,64):
				wrong_desc.append(len(apc_bins[i]))
			wrong_desc.append(b[now])
			wrong_desc.append(b_o[now])
			wrong_saw = True		
		

def parse_dep(s, apc_bins):
	global papc_bins, aapc_bins
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
	elif s == "6":
		return 6, len(apc_bins[1]) + 12
	elif s == "7":
		return 7, len(aapc_bins[1]) + 11
	elif s == "8": # for bin separator
		return 8, 200
	elif s == "9":
		return 9, len(papc_bins[1]) + 6
	elif s == "10":
		return 10, len(apc_bins[1]) + 1
	elif s == "11":
		return 11, len(papc_bins[1]) + 1
	elif s == "12":
		return 12, (len(papc_bins[1])+1)*3+1
	else:
		return -1, 0
	

def fprint(string):
	global index_file
	print string
	index_file.write(string + "\n")

def fprint_(string):
	global index_file
	print string
	index_file.write(string)	
	
def fprint_close():
	global index_file
	index_file.close()
	
def get_previous_block(b, n):
	if n<=0:
		return [0]*64
	else:
		return b[n-1]	

def generate_blocks(folder):
	f_blocks = glob.glob(folder + "/*.block")
	f_jpgs = glob.glob(folder + "/*.jpg")
	if len(f_blocks) != len(f_jpgs):
		os.system("rm *.blocks")
	else:
		return
	
	for f in f_jpgs:
		name = f[f.rfind("/") + 1 : ]
		sys.stdout.flush()
		cmd = "/opt/libjpeg-turbo/bin/jpegtran -outputcoef " + folder + "/" + name + ".block " + f + " temp.out"
		os.system(cmd)
	os.system("rm temp.out")

def get_deps_from_file(f):
	ls = open(f).readlines()[0].split(" ")
	return ls[0], ls[1]
	
def get_deps_from_file_partial(f):
	ls = open(f).readlines()[0].split(" ")
	return ls[0], ls[1], ls[2], ls[3]
	
def get_max_pos_value(folder, comp):
	fprint("calculating max_pos_value...")
	generate_blocks(folder)
	files = glob.glob(folder + "/*.block")
	f = ""
	for i in files:
		f += i + "|"
	blocks = get_blocks_all_in_bits(f[:-1], comp)
	ret = {}
	for x in range(0, 64):
		m = 1 # at least 1
		n = 0
		for ii in range(len(blocks)):
			i = abs(blocks[ii][x])
			if i > m:
				m = i
		ret[x] = m
	return ret
	
def record_code_temp(bs, now, c, start, end, oc, oc_2, dep1, dep2, b_mcu1, b_mcu2):
	global look_backward_block, look_forward_coef, pre_bins, avg_coef
	global max_pos1, max_pos2
	b = bs[now]
	if dep1=="1":
		v = get_avg_pre_coef(bs[now], start)
		oc[start][int(v*pre_bins)] += 1
	elif dep1=="10":
		ma, su = get_energy_level(bs, now, start, end)
		oc[start][int(su*1.0/ma*pre_bins)] += 1
		
	# for dimension 2
	if dep2 == "9":
		seen, ma, su = get_previous_blocks_coef(bs, now, start, end)
		if not seen:
			pass
			#oc_2[start][0] += 1
		else:
			oc_2[start][int(su*1.0/ma*pre_bins)] +=1
	elif dep2 == "11":
		ma, su = get_mcu_energy_level(b_mcu1, b_mcu2, now, start, end)
		oc_2[start][int(su*1.0/ma*pre_bins)] += 1
	elif dep2=="5":
		su = 0
		ma = 0
		n = 0
		pos = -1
		for x in range(now - 1, max(0, now - 3), -1):
			if bs[x+1][0] > 5:
				break
			for xx in range(start, min(64, start+5)):
				ma += avg_coef[xx]
				if bs[x][xx]:
					su += bs[x][xx]
					#break

#		if not ma:
#			return 21
		if not ma:
			pass
		else:
			oc_2[start][int(su*1.0/ma*pre_bins)] += 1
	
	
def get_avg_coef_bins(folder, comp, dep1, dep2):
	global pre_bins
	global max_pos1, max_pos2
	SIZE1 = pre_bins
	fprint("calculating avg_coef_bins...")
	generate_blocks(folder)
	sep = {}
	oc = {}   #oc for occur, then becomes difference
	oc_2 = {}
	pos = 1
	for i in range(1, 64):
		oc[i] = {}
		oc_2[i] = {}
		for p in range(SIZE1 + 1):
			oc[i][p] = 0
			oc_2[i][p] = 0
	files = glob.glob(folder + "/*.block")
	max_pos1 = get_max_pos_value_func(folder, "1")
	max_pos2 = get_max_pos_value_func(folder, "2")		
	for f in files:
		bs = get_blocks_all_in_bits(f, comp)
		b_mcu1 = get_blocks_all_in_bits(f, "1")
		b_mcu2 = get_blocks_all_in_bits(f, "2")
	
		for ii in range(len(bs)):
			b = bs[ii]
			r = 0
			pos = 1
			for i in range(1, 64):
				if b[i] == 0:
					r += 1
					continue
				while (r > 15):
					record_code_temp(bs, ii, 0xf0, pos, pos + 15, oc, oc_2, dep1, dep2, b_mcu1, b_mcu2)
					pos += 16
					r -= 16
				record_code_temp(bs, ii, (r << 4) + b[i], pos, i, oc, oc_2, dep1, dep2, b_mcu1, b_mcu2)
				pos = i + 1
				r = 0
			if r > 0:
				record_code_temp(bs, ii, 0, pos, 63, oc, oc_2, dep1, dep2, b_mcu1, b_mcu2)
	sep = {}
	sep_2 = {}
	for i in range(1, 64):
		tc = {}
		tt = 0
		for ii in range(SIZE1 + 1):
			tc[ii] = deepcopy(oc[i][ii])
			tt += oc[i][ii]
			
		t = SIZE1 + 1
		s = []
		for ii in range(SIZE1 + 1):
			s.append([ii])
		now = 0
		tail = SIZE1
		while True:
			a = tc[now]
			#print a,
			if a<tt/20.0 or tt==0:
				merged = tc[now] + tc[now+1]
				tc[now] = deepcopy(merged)
				s[now] += s[now + 1]
				del s[now + 1]

				for ii in range(now + 1, len(s) - 1):
					tc[ii] = deepcopy(tc[ii + 1])
				tail = len(s) - 1
				if now >= tail:
					break
			else:
				now += 1
				if now >= tail:
					break
		t = len(s)
		tt = []
		for ii in range(len(s) - 1):
			tt.append(s[ii][len(s[ii]) - 1]*1.0/SIZE1)
		if tt==[]:
			tt.append(0.0)
		for ii in range(20 - len(tt)):
			tt.append(tt[len(tt) - 1])
		sep[i] = tt
	for i in range(1, 64):
		tc = {}
		tt = 0
		for ii in range(SIZE1 + 1):
			tc[ii] = deepcopy(oc_2[i][ii])
			tt += oc_2[i][ii]
			
		t = SIZE1 + 1
		s = []
		for ii in range(SIZE1 + 1):
			s.append([ii])
		now = 0
		tail = SIZE1
		while True:
			a = tc[now]
			#print a,
			if a<tt/20.0 or tt == 0:
				merged = tc[now] + tc[now+1]
				tc[now] = deepcopy(merged)
				s[now] += s[now + 1]
				del s[now + 1]

				for ii in range(now + 1, len(s) - 1):
					tc[ii] = deepcopy(tc[ii + 1])
				tail = len(s) - 1
				if now >= tail:
					break
			else:
				now += 1
				if now >= tail:
					break
		t = len(s)
		tt = []
		for ii in range(len(s) - 1):
			tt.append(s[ii][len(s[ii]) - 1]*1.0/SIZE1)
		if tt == []:
			tt.append(0.0)
		if (len(tt) > 20):
			print "*", tt
			print s
			print tc
			print oc[i]
		for ii in range(20 - len(tt)):
			tt.append(tt[len(tt) - 1])
		sep_2[i] = tt
	return sep, sep_2

def get_max_pos_value_func(image_folder, comp):
	ret = 0
	if os.path.isfile(image_folder + "/max_pos_value_" + comp):
		pkl_file = open(image_folder + "/max_pos_value_" + comp)
		ret = pickle.load(pkl_file)
		pkl_file.close()
	else:
		print "regenerating max_pos_values..."
		ret = get_max_pos_value(image_folder, comp)
		pkl_file = open(image_folder + "/max_pos_value_" + comp, 'wb')
		pickle.dump(ret, pkl_file)
		pkl_file.close()
	return ret

	
def init(comp, image_folder, tbl_folder, dep1, dep2):
	global code, dc_code, avg_coef, apc_bins, papc_bins, avg_actual_coef, aapc_bins, wrong_keys, avg_coef_max, max_pos1, max_pos2
	if dep1 != "-1" or dep2 != "-1":
		if os.path.isfile("bin_separator_600_"+comp):
			pkl_file = open("bin_separator_600_"+comp, 'rb')
			aapc_bins = pickle.load(pkl_file)
			pkl_file.close()

		# max value for each position
		if os.path.isfile(image_folder + "/max_pos_value_" + comp):
			pkl_file = open(image_folder + "/max_pos_value_" + comp)
			avg_coef = pickle.load(pkl_file)
			pkl_file.close()
		else:
			print "regenerating max_pos_values..."
			avg_coef = get_max_pos_value(image_folder, comp)
			pkl_file = open(image_folder + "/max_pos_value_" + comp, 'wb')
			pickle.dump(avg_coef, pkl_file)
			pkl_file.close()
		f = open(tbl_folder + "/plain_max_pos_value_" + comp, 'wb')
		for x in avg_coef:
			f.write(str(x) + ": " + str(avg_coef[x]) + "\n")
		f.close()
		avg_coef_max = [0]*64
		for i in range(1, 64):
			tt = 0
			for j in range(1, i+1):
				tt += avg_coef[j]
			avg_coef_max[i] = tt
		print avg_coef_max
		os.system("cp " + image_folder + "/*max_pos_value_" + comp + " " + tbl_folder + "/")

		dep2_ = dep2
		if dep2 == "12":
			dep2_ = "9"
		# coef bins
		if os.path.isfile(image_folder + "/coef_bins_" + str(dep1) + "_" + comp) and os.path.isfile(image_folder + "/coef_bins_" + str(dep2_) + "_" + comp):
			pkl_file = open(image_folder + "/coef_bins_" + str(dep1) + "_" + comp)
			apc_bins = pickle.load(pkl_file)
			pkl_file.close()
			pkl_file = open(image_folder + "/coef_bins_"  + str(dep2_) + "_" + comp)
			papc_bins = pickle.load(pkl_file)
			pkl_file.close()
		else:
			print "regenerating coef_bins..."
			apc_bins, papc_bins = get_avg_coef_bins(image_folder, comp, dep1, dep2_)
			pkl_file = open(image_folder + "/coef_bins_" + str(dep1) + "_" + comp, 'wb')
			pickle.dump(apc_bins, pkl_file)
			pkl_file.close()
			pkl_file = open(image_folder + "/coef_bins_" + str(dep2_) + "_" + comp, 'wb')
			pickle.dump(papc_bins, pkl_file)
			pkl_file.close()
		f = open(tbl_folder + "/plain_coef_bins_" + str(dep1) + "_" + comp, 'wb')
		for x in apc_bins:
			f.write(str(x) + ": ")
			for y in range(len(apc_bins[x])):
				f.write(str(apc_bins[x][y]) + " ")
			f.write("\n")
		f.close()		
		f = open(tbl_folder + "/plain_coef_bins_"  + str(dep2_) + "_" + comp, 'wb')
		for x in papc_bins:
			f.write(str(x) + ": ")
			for y in range(len(papc_bins[x])):
				f.write(str(papc_bins[x][y]) + " ")
			f.write("\n")
		f.close()
		os.system("cp " + image_folder + "/*coef_bins_" + str(dep1) + "_" + comp + " " + tbl_folder + "/")		
		os.system("cp " + image_folder + "/*coef_bins_" + str(dep2_) + "_" + comp + " " + tbl_folder + "/")		

	if comp == "0":
		code = get_luminance_codes()
		dc_code = bits_dc_luminance
		avg_actual_coef = avg_actual_coef_600_0
	else:
		code = get_chrominance_codes()
		dc_code = bits_dc_chrominance
		avg_actual_coef = avg_actual_coef_600_0
	
	wrong_keys = 0
	max_pos1 = get_max_pos_value_func(image_folder, "1")
	max_pos2 = get_max_pos_value_func(image_folder, "2")	

def init_testing(comp, tbl_folder, dep1, dep2):
	global code, dc_code, avg_coef, apc_bins, papc_bins, avg_actual_coef, aapc_bins, avg_coef_max, max_pos1, max_pos2
	if dep1 != "-1" or dep2 != "-1":
		if os.path.isfile("bin_separator_600_"+comp):
			pkl_file = open("bin_separator_600_"+comp, 'rb')
			aapc_bins = pickle.load(pkl_file)
			pkl_file.close()

		# max value for each position
		if os.path.isfile(tbl_folder + "/max_pos_value_" + comp):
			pkl_file = open(tbl_folder + "/max_pos_value_" + comp)
			avg_coef = pickle.load(pkl_file)
			pkl_file.close()
		
		else:
			print "no max_pos_values..."
			exit()
		avg_coef_max = [0]*64
		for i in range(1, 64):
			tt = 0
			for j in range(1, i+1):
				tt += avg_coef[j]
			avg_coef_max[i] = tt
		
		dep2_ = dep2
		if dep2 == "12":
			dep2_ = "9"
		# coef bins
		if os.path.isfile(tbl_folder + "/coef_bins_" + str(dep1) + "_" + comp):
			pkl_file = open(tbl_folder + "/coef_bins_" + str(dep1) + "_" +  comp)
			apc_bins = pickle.load(pkl_file)
			pkl_file.close()
		else:
			print "no coef_bins..."
			exit()

		if os.path.isfile(tbl_folder + "/coef_bins_" +  str(dep2_) + "_" + comp):
			pkl_file = open(tbl_folder + "/coef_bins_"  + str(dep2_) + "_" + comp)
			papc_bins = pickle.load(pkl_file)
			pkl_file.close()
		else:
			print "no coef_bins_p..."
			exit()

	if comp == "0":
		code = get_luminance_codes()
		dc_code = bits_dc_luminance
		avg_actual_coef = avg_actual_coef_600_0
	else:
		code = get_chrominance_codes()
		dc_code = bits_dc_chrominance
		avg_actual_coef = avg_actual_coef_600_0
	max_pos1 = get_max_pos_value_func(tbl_folder, "1")
	max_pos2 = get_max_pos_value_func(tbl_folder, "2")
		
def bin_separator(bins, s, final_bin_number, total_samples):
	now = 0
	tail = len(bins)
	
	while True:
		a = bins[now]
		#print a,
		if a<total_samples*1.0/final_bin_number:
			merged = bins[now] + bins[now+1]
			bins[now] = deepcopy(merged)
			s[now] += s[now + 1]
			del s[now + 1]

			for ii in range(now + 1, len(s) - 1):
				bins[ii] = deepcopy(bins[ii + 1])
			tail = len(s) - 1
			if now >= tail:
				break
		else:
			now += 1
			if now >= tail:
				break
	t = len(s)
	tt = []
	for ii in range(len(s) - 1):
		tt.append(s[ii][len(s[ii]) - 1])
	for ii in range(final_bin_number - len(tt)):
		tt.append(tt[len(tt) - 1])
	t = len(s)
	return tt

def all_zero_block(b):
	for i in range(1, 64):
		if b[i] != 0:
			return False
	return True

def get_dc_dependency(b_o, b, i):
	x = 2
	t = 0
	s = 0
	for ii in range(x):		
		s += get_previous_block(b, i-ii)[0]
		if get_previous_block(b_o, i-ii)[0] < 0:
			t-=1
		elif get_previous_block(b_o, i-ii)[0] > 0:
			t+=1
	s = s/x
	if t<=-1:
		s += 12
	elif t>=1:
		s += 24
	return s
	
dep1 = 0
dep2 = 0
apc_bins = 0   # 1st dependency
papc_bins = 0  # 2nd dependency
aapc_bins = 0
avg_coef = 0
avg_coef_max = 0
avg_actual_coef = 0
index_file = 0
code = 0
dc_code = 0
wrong_keys = 0
wrong_desc = 0
wrong_saw = False
look_backward_block = 3 # change back to 3
look_forward_coef = 5 
pre_bins = 500
max_pos1 = 0
max_pos2 = 0
