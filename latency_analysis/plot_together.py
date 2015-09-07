import matplotlib
matplotlib.use('Agg')
import os, sys, glob, commands, pickle
import matplotlib.pyplot as plt
from pylab import *
import numpy

def pdf_cdf(b):
	c = []
	pre = 0
	for x in b:
		pre += x
		c.append(pre)
	return c

#OB_x = [1,3,5,7,10,30,50,70,100,300,500,700,1000,3000,5000,7000,10000,30000,50000,70000,100000,300000]
#OB_y = [0.0198586,0.137056,0.14988,0.16166,0.215622,0.875385,0.949121,0.969343,0.980389,0.991751,0.99376,0.994784,0.995669,0.998924,0.999957,0.999999,1,1,1,1,1,1] 

fname = []
for x in range(1, len(sys.argv)):
	fname.append(sys.argv[x])

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_ylabel("CDF")
ax.set_xlabel("Latency (ms)")
ax.grid()
ax.set_ylim([0,1.1])
legend = []
for f in fname:
	#with open(f.split(".")[0] + ".obj_pdf", 'rb') as f_in:
	with open(f, 'rb') as f_in:
		x, y = pickle.load(f_in)
		legend.append(f.split(".")[0])
	ax.plot(x, pdf_cdf(y))
#ax.plot(OB_x, OB_y)
#legend.append("Origin to Backend")
ax.legend(legend, 4)
ax.set_xlim([0, 1800])
#ax.set_xscale("log")
#ax.set_yscale("log")

savefig("plot_together.png")
plt.close("all")
