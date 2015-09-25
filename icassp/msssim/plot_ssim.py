import matplotlib
matplotlib.use('Agg')
import os, sys, glob, commands, pickle, re
import matplotlib.pyplot as plt
from pylab import *
import numpy
import matplotlib.gridspec as gridspec
from plot import *

def get_lromp():
	ls = open("lromp.out").readlines()
	x = []
	y1 = []
	y2 = []
	for l in ls:
		q = re.match("2 (.*) size (.*) psnr (.*) ssim (.*)", l)
		x.append(float(q.group(2)))
		y1.append(float(q.group(3)))
		y2.append(float(q.group(4)))
	print x
	print y1
	print y2
	return x, y1, y2

def get_raw():
	ls = open("icassp_fromraw.out").readlines()
	x = []
	y1 = []
	y2 = []
	flag = False
	for l in ls:
		q = re.match("size (.*) psnr (.*) ssim (.*)", l)
		if q == None:
			if l.find("75") != -1:
				flag = True
			continue
		if flag == True:
			a = float(q.group(1))
			b = float(q.group(2))
			c = float(q.group(3))
			flag = False
		x.append(float(q.group(1)))
		y1.append(float(q.group(2)))
		y2.append(float(q.group(3)))
	print x
	print y1
	print y2
	return x, y1, y2, a, b, c

def get_75():
	ls = open("icassp_from_q.out").readlines()
	x = []
	y1 = []
	y2 = []
	for l in ls:
		q = re.match("size (.*) psnr (.*) ssim (.*)", l)
		if q == None:
			continue
		x.append(float(q.group(1)))
		y1.append(float(q.group(2)))
		y2.append(float(q.group(3)))
	print x
	print y1
	print y2
	return x, y1, y2

x_lromp, lromp_psnr, lromp_ssim = get_lromp()
x_raw, raw_psnr, raw_ssim, a,b,c = get_raw()
x_75, _75_psnr, _75_ssim = get_75()

x_lromp = [a] + x_lromp
lromp_psnr = [b] + lromp_psnr
lromp_ssim = [c] + lromp_ssim

x_75 = [a] + x_75
_75_psnr= [b] + _75_psnr
_75_ssim = [c] + _75_ssim

fig = plt.figure()

#ax = plt.subplot(gs[0])
ax2 = plt.subplot(111)

#ax = fig.add_subplot(121)
#ax2 = fig.add_subplot(122)
ax2.set_ylabel("PSNR", fontsize = label_font_size)
ax2.set_xlabel("Size", fontsize = label_font_size)
ax2.plot(x_lromp, lromp_psnr, "-+")
ax2.plot(x_raw, raw_psnr, "-x")
ax2.plot(x_75, _75_psnr, "-o")
#ax.set_title("Saving=%.3f, Decoding=%.3fMS"%(saving, decoding))
ax2.grid()
ax2.set_xlim([120000,220000])
ax2.set_ylim([32,36])
#legend = []
#ax2.set_ylim(ax2.get_ylim()[::-1])
#ax2.set_xlim([1.12*ax2_minx,1.12*ax2_maxx])
#ax2.set_xlim([-800, 600])

#ax.set_xlim([0,4500])

#ax.set_xticks([0,1000,2000,3000,4000])
#ax2.set_xticks([-500,0,500])
#ax2.set_yticklabels([])
#ax2.set_yticklabels(["0","0.9","0.99"])



#ax.plot(OB_x, OB_y)
#legend.append("Origin to Backend")

#legend[legend.index("L-ROMP-Same-Size")] = "L-ROMP'"

ax2.legend(["lromp", "raw", "75"], 3, fontsize=legend_font_size)
#ax.legend(["W/o Re-Compression", "W/ Re-Compression"], 4)

#ax.set_xscale("log")
#ax.set_yscale("log")

set_plt(plt)
#set_ax(ax)
set_ax(ax2)


savefig("plot_ssim.png")#final_%d_.png"%(tested_file_size))
savefig("plot_ssim.eps")#%(tested_file_size))

plt.tight_layout()
plt.close("all")
