import sys, os, heapq, glob, operator, pickle
from operator import itemgetter
from copy import *
import lib_new as lib

#if len(sys.argv) == 1:
#	print "usage: python runsize.py size(600, 1200), component_number(0,1,2) start_learn_image(1-100), end_learn_image(1-100), end_test_image(1-100), dep. 1(0:DC, 1:avg_pre_coef, 2:avg_pre_block_coef, 3:pre_block_coef, r:last_block_eob, 5:pre_blocks_sign), dep. 2(0:DC, 1:avg_pre_coef, 2:avg_pre_block_coef, 3:pre_block_coef, 4:last_block_eob, 5:pre_blocks_sign)"
#	exit()

quant = {}
quant["0"] = [16,  11,  10,  16,  24,  40,  51,  61,
  12,  12,  14,  19,  26,  58,  60,  55,
  14,  13,  16,  24,  40,  57,  69,  56,
  14,  17,  22,  29,  51,  87,  80,  62,
  18,  22,  37,  56,  68, 109, 103,  77,
  24,  35,  55,  64,  81, 104, 113,  92,
  49,  64,  78,  87, 103, 121, 120, 101,
  72,  92,  95,  98, 112, 100, 103,  99]

quant["1"] = [17,  18,  24,  47,  99,  99,  99,  99,
  18,  21,  26,  66,  99,  99,  99,  99,
  24,  26,  56,  99,  99,  99,  99,  99,
  47,  66,  99,  99,  99,  99,  99,  99,
  99,  99,  99,  99,  99,  99,  99,  99,
  99,  99,  99,  99,  99,  99,  99,  99,
  99,  99,  99,  99,  99,  99,  99,  99,
  99,  99,  99,  99,  99,  99,  99,  99]

quant["2"] = quant["1"]

jpeg_natural = [0,  1,  8, 16,  9,  2,  3, 10,
 17, 24, 32, 25, 18, 11,  4,  5,
 12, 19, 26, 33, 40, 48, 41, 34,
 27, 20, 13,  6,  7, 14, 21, 28,
 35, 42, 49, 56, 57, 50, 43, 36,
 29, 22, 15, 23, 30, 37, 44, 51,
 58, 59, 52, 45, 38, 31, 39, 46,
 53, 60, 61, 54, 47, 55, 62, 63,
 63, 63, 63, 63, 63, 63, 63, 63]

def get_code(x, code):
	s = x&15
	r = x>>4
	ret = 0
	while r>15:
		r-=16
		ret += code[0xf0]
	ret += code[(r<<4)+s]
	return ret

def get_r_l(x, code):
	l = " (" + str(get_code(x,code)) + ")"
	if x:
		return "r_" + str(x>>4) + "_l_" + str(x&15) + l
	else:
		return "EOB" + l

def zero_off(b, b_o, code, ci, sf):
	global thre
	modified = 0
	r = 0
	pos = 1

	r_l = []
	p = []
	for i in range(1, 64):
		if b[i] == 0:
			r += 1
			continue
		r_l.append((r<<4)+b[i])
		p.append(i)
		pos = i + 1
		r = 0
	if r > 0:
		r_l.append(0)
		p.append(-1)
	
	i = -1
	while i + 1 < len(r_l):
		i += 1
		be = ""
		af = ""
		af_code = 0
		x = r_l[i]
		if (x & 15) != 1:
			continue
		
		if i < len(r_l)-1:
			y = r_l[i+1]
			diff = get_code(x, code)+get_code(y,code)+1 # e.g., run-2-length-1, run-3-length-1; or, run-2-length-1, EOB; 1 is for the magnitude bits of +1 or -1;
			be = get_r_l(x, code) + " " + get_r_l(y, code) + " + 1 bit"
			if y==0:
				diff -= get_code(0, code)
				af = get_r_l(y, code)
			else:
				s = y & 15
				if s==0:
					diff = -1
				else:
					r_ = ((x>>4) + (y>>4) + 1)
					diff -= get_code((r_ << 4) + s, code)
					af = get_r_l((r_ << 4) + s, code)
					af_code = (r_ << 4) + s
		else:
			be = get_r_l(x, code) + " + 1 bit"
			af = get_r_l(0, code)
			af_code = 0
			diff = get_code(x,code)+1-get_code(0, code)
		#if diff >= thre*pow((quant[ci][jpeg_natural[p[i]]]*sf+50)/100, 2):
		if diff >= thre*pow(quant[ci][jpeg_natural[p[i]]], 2):
		#if diff >= thre:
			if modified == 0:
				#print " "
				#print " "
				#modified = True
				pass
			modified += 1
			#print "comp", ci, ":"
			#print b
			#print b_o
			#print "\t", p[i], ":", diff, "    before", be, " after ", af
			b[p[i]] = 0
			b_o[p[i]] = 0
			
			if i<len(r_l)-1:			
				r_l.pop(i)
				p.pop(i)
				r_l[i] = af_code
			else:
				r_l[i] = af_code
				p[i] = -1
			i -= 1
	return modified

if len(sys.argv) != 5:
	print "usage: python lossy_zerooff.py [INPUT.block] [OUTPUT.block] [GAIN BITS THRESHOLD] [QUALITY]"
	exit()

in_ = sys.argv[1]
out_ = sys.argv[2]
thre = float(sys.argv[3])
quality = int(sys.argv[4])
if quality<50:
	scale_factor = 5000/quality
else:
	scale_factor = 200-quality*2

l_in = open(in_).readlines()
l_out = open(out_, "w")

total_modified = 0
for l in l_in:
	s = l[:-2].split(" ")
	b = []
	b_o = []
	if s[0] == "0" + ":":
		code = lib.get_luminance_codes()
	else:
		code = lib.get_chrominance_codes()
	last_dc = 0
	for j in range(1, len(s)):
		if j==1:
			b.append(lib.get_bits(abs(int(s[j]) - last_dc)))
			b_o.append(int(s[j]))
			last_dc = int(s[j])
		else:
			b.append(lib.get_bits(abs(int(s[j]))))
			b_o.append(int(s[j]))

	total_modified += zero_off(b, b_o, code, s[0].split(":")[0], scale_factor)
	l_out.write(s[0] + " ")
	for x in b_o:
		l_out.write(str(x)+" ")
	l_out.write("\n")
l_out.close()
print total_modified
