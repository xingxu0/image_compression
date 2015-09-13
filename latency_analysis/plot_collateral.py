import matplotlib
matplotlib.use('Agg')
import os, sys, glob, commands, pickle
import matplotlib.pyplot as plt
from pylab import *
import numpy
import matplotlib.gridspec as gridspec

# add how many MS to backend?
bad_origin = 0
bad_backend = 0

# hit ratio improvement for every 1% increment of cache size,
# 50% extra cache increaese 3.6% hit ratio
edge_cache_hr = 0.0036/5

# 50% extra cache increaese 5.5% hit ratio
origin_cache_hr = 0.0055/5

edge_current_hr = 0.58
origin_current_hr = 0.32

measured_file_size = 100000


def pdf_cdf(b):
	c = []
	pre = 0
	for x in b:
		pre += x
		c.append(pre)
	return c

def get_cache(i):
	global hr, proc, l, x_min, x_max
	x = []
	y = []
	flag = True
	t_ = 0.0
	for a in range(x_min, x_max+1):
		x.append(a + proc[i])
		p = 0.0
		for ii in range(len(l)):
			if a in l[ii]:
				p += hr[i][ii]*l[ii][a]
		y.append(p)
		t_ += p
		if flag and t_>=0.5:
			print i, ":",hr[i],proc[i], p,a+proc[i]
			flag = False


	print t_
	return x, y



hr = [[1,0,0], [0,1,0],[0,0,1]]
hr = [[0.1,0.3,0.6],[0.5,0.3,0.2]]
hr = [[0.1,0.3,0.6],[0.1,0.3,0.6]]
# edge cache: 1% higher : 58% -> 59%
# origin cache: 1.8% higher : 31.67% -> 33.47%
hr = [[0.580,0.133,0.287],[0.580,0.133,0.287], [0.590,0.137,0.273]]
proc = [0,19.2,19.2]

c_r = [0, 5, 10,15,20,25,30,35,40,45,50]

hr =[]
proc = []

#edge_current_hr, origin_current_hr = get_

cu = [edge_current_hr, (1-edge_current_hr)*origin_current_hr]
cu.append(1-cu[0]-cu[1])
hr.append(cu)
proc.append(0)
legend = ["Facebook"]
y = [[],[],[]]
for s in c_r:
	#legend.append(s[0]+": "+s[1]+" "+s[2])
	#legend.append(s[0])

	saving = 10000/(100-float(s))-100
	t__1 = edge_current_hr + edge_cache_hr*saving
	t__2 = origin_current_hr + origin_cache_hr*saving
	cu = [t__1, (1-t__1)*t__2]
	y[0].append(t__1)
	y[1].append((1-t__1)*t__2)
	y[2].append(1-t__1-(1-t__1)*t__2)


fig = plt.figure()

ax = fig.add_subplot(111)
#ax2 = fig.add_subplot(122)
ax.set_ylabel("Percentage")
ax.set_xlabel("Compression Ratio (%)")

wid = 0.5
xxx = []
for i in range(len(c_r)):
	xxx.append(i-wid/2)
ax.bar(xxx, y[0], wid, color ="r")
ax.bar(xxx, y[1], wid, bottom=y[0], color="y")
yyy = []
for i in range(len(y[1])):
	yyy.append(y[1][i]+y[0][i])
ax.bar(xxx, y[2], wid, bottom=yyy, color="b")
print y[0]
print y[1]
print y[2]
#ax2.set_yscale("log")
#ax2.set_ylim(ax2.get_ylim()[::-1])
#ax.set_xlim([0,x_lim])

ax.set_xticks(range(len(c_r)))
ax.set_xticklabels(["0","5","10","15","20","25","30","35","40","45","50"])

ax.legend(["edge","origin","backend"], 4)

#ax.plot(OB_x, OB_y)
#legend.append("Origin to Backend")
#ax.legend(["W/o Re-Compression", "W/ Re-Compression"], 4)

#ax.set_xscale("log")
#ax.set_yscale("log")

savefig("plot_serving_reduction.png")

plt.tight_layout()
plt.close("all")
