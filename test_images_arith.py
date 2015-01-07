import os, commands, re, sys
import matplotlib.pyplot as plt
from pylab import *

folders = ['100', '200', '300', '400', '600', '800', '1000', '1200']
folders = ['600']

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
for f in folders:
	total_arith = 0
	total_actual = 0
	total_encoding_time = 0
	total_decoding_time = 0
	for i in range(1, 101):#101):
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -arithmetic images/" + f + "_Q75/" + str(i) + ".jpg temp.jpg")
		print c
		# sample output: Total saving: 134751 bits\nOriginal filesize: 106207, encoded filesize: 89350, saving: 0.158718\nTotal time elapsed : 65678 us'
		m = re.match("(.*)\narith bytes count: (.*)\nhuffman bytes total: (.*)\n(.*)", c[1])
		arith_bits = int(m.group(2))
		actual_bits = int(m.group(3))
		jpg_opt_size = int(m.group(2))
		print arith_bits, actual_bits
	total_arith += arith_bits
	total_actual += actual_bits
print total_arith, total_actual, (total_actual - total_arith)*1.0/total_actual