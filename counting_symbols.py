# count the symbols for different image sizes, the point of doing this is we want to get the proof of sublinear performance of our codec

import sys, copy, os, heapq, glob, operator, pickle, lib
from operator import itemgetter
import matplotlib.pyplot as plt
from pylab import *
	
def count_symbols(folder):
	s = 0
	files = glob.glob(folder + "/*.block")
	for f in files:
		for c in range(3):
			block = lib.get_blocks_all_in_bits(f, str(c))
			for ii in range(len(block)):
				s += 2
				b = block[ii]
				n = 63
				while (b[n] == 0 and n>0):
					n-=1
				for x in range(1, n + 1):
					if b[x] !=0:
						s += 1
	return s
					
					
					

folders = ['100', '200', '300', '400', '600', '800', '1000', '1200']
x= []
symbols=[]
symbols_=[]
base = 0
for f in folders:
	print f
	ss = count_symbols("../../image_compression/images/" + f + "_Q75")
	x.append(int(f)*int(f))
	symbols.append(ss)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(x, symbols, '-sr')
ii = -1
for f in folders:
	ii += 1
	ff = int(f)
	xx = []
	yy = []
	x1 = ff*ff - 150000
	x2 = ff*ff + 150000
	xx.append(x1)
	xx.append(ff*ff)
	xx.append(x2)
	yy.append(symbols[ii]*1.0/ff/ff*x1)
	yy.append(symbols[ii])
	yy.append(symbols[ii]*1.0/ff/ff*x2)
	ax.plot(xx, yy, '--k')
	
ax.plot(x, symbols, '-sr')
ax.set_xlabel("Number of Pixels")
ax.set_ylabel("Number of Symbols")
ax.legend(['symbols', 'linear bound'], 4)
ax.set_xlim([0, 2300000])
ax.set_ylim([0, symbols[len(symbols)-1]*1.2)
savefig("count_symbols.png")
