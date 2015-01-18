import os, commands, re, sys
import matplotlib.pyplot as plt
from pylab import *

folders = ['100', '200', '300', '400', '600', '800', '1000', '1200']
folders = ['600']
#folders = ['1200']

x = []
y_encoding = []
y_decoding = []
encoding = []
decoding = []
gain_ratio = []

first_seen = False
base_encode = 0
base_decode = 0
base_x = 0
fig = plt.figure()
ax = fig.add_subplot(111)
total_arith = 0
total_raw = 0
total_1 = 0
for f in folders:
	total_encoding_time = 0
	total_decoding_time = 0
	for i in range(1, 101):#101):
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -arithmetic images/" + f + "_Q75/" + str(i) + ".jpg temp.jpg")
		print c
		# sample output: Total saving: 134751 bits\nOriginal filesize: 106207, encoded filesize: 89350, saving: 0.158718\nTotal time elapsed : 65678 us'
		m = re.match("(.*)\nxxx (.*), (.*), (.*)", c[1], re.DOTALL)
		arith_bits = int(m.group(2))
		raw_bits = int(m.group(3))
		one_bits = int(m.group(4))
		print arith_bits, raw_bits, one_bits
		total_arith += arith_bits
		total_raw += raw_bits
		total_1 += one_bits
print total_arith, total_raw, total_1
