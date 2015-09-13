import matplotlib
matplotlib.use('Agg')
import os, sys, glob, commands, pickle
import matplotlib.pyplot as plt
from pylab import *
import numpy
import matplotlib.gridspec as gridspec

# add how many MS to backend?
bad_origin = 0
bad_backend = 300

# hit ratio improvement for every 1% increment of cache size,
# 50% extra cache increaese 3.6% hit ratio
edge_cache_hr = 0.0036/5*2

# 50% extra cache increaese 5.5% hit ratio
origin_cache_hr = 0.0055/5*2

edge_current_hr = 0.30
origin_current_hr = 0.20

measured_file_size = 100000
tested_file_size = int(sys.argv[len(sys.argv)-1])


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



scheme_number = len(sys.argv) - 2
schemes = []
for i in range(scheme_number):
	t = sys.argv[i + 1].split(",")
	schemes.append(t)
print schemes

#saving = float(sys.argv[1])
#decoding = float(sys.argv[2])

#OB_x = [1,3,5,7,10,30,50,70,100,300,500,700,1000,3000,5000,7000,10000,30000,50000,70000,100000,300000]
#OB_y = [0.0198586,0.137056,0.14988,0.16166,0.215622,0.875385,0.949121,0.969343,0.980389,0.991751,0.99376,0.994784,0.995669,0.998924,0.999957,0.999999,1,1,1,1,1,1] 

hr = [[1,0,0], [0,1,0],[0,0,1]]
hr = [[0.1,0.3,0.6],[0.5,0.3,0.2]]
hr = [[0.1,0.3,0.6],[0.1,0.3,0.6]]
# edge cache: 1% higher : 58% -> 59%
# origin cache: 1.8% higher : 31.67% -> 33.47%
hr = [[0.580,0.133,0.287],[0.580,0.133,0.287], [0.590,0.137,0.273]]
proc = [0,19.2,19.2]


hr =[]
proc = []
cu = [edge_current_hr, (1-edge_current_hr)*origin_current_hr]
cu.append(1-cu[0]-cu[1])
hr.append(cu)
proc.append(0)
legend = ["Facebook"]
for s in schemes:
	#legend.append(s[0]+": "+s[1]+" "+s[2])
	legend.append(s[0])

	saving = float(s[1])
	t__1 = edge_current_hr + edge_cache_hr*saving
	t__2 = origin_current_hr + origin_cache_hr*saving
	cu = [t__1, (1-t__1)*t__2]
	cu.append(1-cu[0]-cu[1])
	hr.append(cu)
	proc.append(float(s[2]))

print "hr:",hr
print "proc:",proc

fname = ["edge_%d.obj_pdf_gen"%(tested_file_size),"origin_%d.obj_pdf_gen"%(tested_file_size),"backend_%d.obj_pdf_gen"%(tested_file_size)]
for f in fname:
	if os.path.isfile(f):
		continue
	s = f[:f.find("_")]
	os.system("python estimate_latency.py %s_1st.obj_pdf %s_transfer.obj_pdf %s_%d.obj_pdf_gen %f"%(s, s, s, tested_file_size, tested_file_size*1.0/measured_file_size))
#for x in range(1, len(sys.argv)):
#	fname.append(sys.argv[x])
fig = plt.figure()

gs = gridspec.GridSpec(1, 2,width_ratios=[2,1])

ax = plt.subplot(gs[0])
ax2 = plt.subplot(gs[1])

#ax = fig.add_subplot(121)
#ax2 = fig.add_subplot(122)
ax.set_ylabel("CDF")
ax.set_xlabel("Latency (ms)")
#ax.set_title("Saving=%.3f, Decoding=%.3fMS"%(saving, decoding))
ax.grid()
#ax.set_xlim([0,300])
#legend = []
l = []
i = 0
x_min = 1000000
x_max = -1 
for f in fname:
	l.append({})
	with open(f.split(".")[0] + ".obj_pdf_gen", 'rb') as f_in:
		x, y = pickle.load(f_in)
		if f == fname[2]:
			for ii in range(len(x)):
				x[ii] += bad_backend 
		if f == fname[1]:
			for ii in range(len(x)):
				x[ii] += bad_origin
		print f, min(x), max(x)
		print x[:10],y[:10]
		x_min = min(x_min, min(x))
		x_max = max(x_max, max(x))
		for j in range(len(x)):
			l[i][int(x[j])] = y[j]
	i += 1
		#legend.append(f.split(".")[0])
	#ax.plot(x, pdf_cdf(y))
x_min = int(x_min)
x_max = int(x_max)
print x_min, x_max
x_all = {}
y_all = {}
x_lim = -1
for i in range(len(hr)):
	x, y = get_cache(i)
	cdf_y = pdf_cdf(y)
	t__ = 0
	
	for ii in range(len(x)):
		if cdf_y[ii]>=1.0:#.999:
			print "abcde", ii
			t__ = ii
			break
		else:
			t__ = ii
	for k in range(len(cdf_y)):
		if cdf_y[k]>.98:
			break
	x_lim = max(x[k], x_lim)

	if i > 0:
		ax.plot(x[:t__], cdf_y[:t__])
	else:
		ax.plot(x[:t__], cdf_y[:t__], "-k")
	x_all[i] = x
	y_all[i] = cdf_y
	'''
	if i == 1:
		x1=x
		y1=cdf_y
	elif i == 2:
		x2=x
		y2=cdf_y
	'''
	#legend.append("%.3f"%(hr[i])+" "+ str(proc[i]))
	#legend.append("[%.3f,%.3f,%.3f]"%(hr[i][0], hr[i][1], hr[i][2])+" "+ str(proc[i]))
'''
l1 = []
n = 1
for i in range(len(x1)):
	if y1[i] >= n/1000.0:
		l1.append(x1[i])
		n += 1
l1.append(x1[len(x1)-1])

l2 = []
n = 1
for i in range(len(x2)):
	if y2[i] >= n/1000.0:
		l2.append(x2[i])
		n += 1
l2.append(x2[len(x2)-1])


print len(l1), len(l2)
print l1
print l2
print "delta:"
xxx = []
yyy = []
for i in range(999):
	xxx.append(i/1000.0)
	print i
	yyy.append(l1[i]-l2[i])

print l1
print l2
print xxx
print yyy
'''

legend2 = []
ax2_minx = 10000
ax2_maxx = -1
for ii in range(1, len(x_all)):
	x2 = x_all[0]
	x1 = x_all[ii]
	y2 = y_all[0]
	y1 = y_all[ii]

	xxx = []
	yyy = []
	last_j = 0
	last_i = 0
	for i in range(len(x1)):
		if i>=1 and y1[i] - y1[last_i] <0.001:
			continue
	#if i >1:
	#	print y1[last_i], y2[last_j], j, x1[last_i]-x2[last_j]
		if y1[i]>.99:
			break

		last_i = i
		j = last_j
		yyy.append(y1[i])
		while j<len(y2) and y2[j] <= y1[i]:
			j += 1
		if j==len(y2):
			xxx.append(x1[i] - x2[j-1])
			last_j = j-1
			continue
		if j ==0:
			xxx.append(x1[i]-x2[0])
			last_j = 0
			continue
		t_inter = (y1[i]-y2[j-1])*1.0/(y2[j] - y2[j-1])
		#print y2[j-1], y1[i], y2[j], t_inter
		#print x2[j-1], (x2[j-1]*t_inter + x2[j]*(1-t_inter)), x2[j] 
		xxx.append(x1[i] - (x2[j-1]*t_inter + x2[j]*(1-t_inter)))
		last_j = j-1
	
	yyyy = []
	# for reverse log_scale
	#for y in yyy:
	#	yyyy.append(1-y)
	#ax2.plot(xxx,yyyy, "-")
	ax2.plot(xxx,yyy,"-")
	legend2.append(schemes[ii-1][0]+"-Facebook")
	ax2_minx = min(ax2_minx, min(xxx))
	ax2_maxx = max(ax2_maxx, max(xxx))
#ax2.set_ylabel("Percentile")
#ax2.legend(legend2)
ax2.set_xlabel("Additional Latency (ms)")
ax2.grid()
#ax2.set_yscale("log")
#ax2.set_ylim(ax2.get_ylim()[::-1])
ax2.set_xlim([1.12*ax2_minx,1.12*ax2_maxx])

ax.set_xlim([0,x_lim])

ax2.set_yticklabels([])
#ax2.set_yticklabels(["0","0.9","0.99"])



#ax.plot(OB_x, OB_y)
#legend.append("Origin to Backend")
ax.legend(legend, 4)
#ax.legend(["W/o Re-Compression", "W/ Re-Compression"], 4)

#ax.set_xscale("log")
#ax.set_yscale("log")

savefig("plot_edge_final_t_%d.png"%(tested_file_size))
savefig("plot_edge_final_t_%d.eps"%(tested_file_size))

plt.tight_layout()
plt.close("all")
