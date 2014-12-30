import sys, copy, os, heapq, glob, operator, pickle, lib, commands
from operator import itemgetter
import matplotlib.pyplot as plt
from pylab import *

#folders = ['100', '200']
folders = ['100', '200', '300', '400', '600', '800', '1000', '1200']
#folders = ['600', '1200']

x = []
opt_size = []
pro_size = []
ari_size = []
diff_ratio_pro = []
diff_ratio_ari = []
for folder in folders:
	size_opt = 0
	size_pro = 0
	size_ari = 0
	files = glob.glob("../../image_compression/images/" + folder + "_Q75" + "/*.jpg")
	#files = glob.glob("../../image_compression/images/" + folder + "_Q92" + "/*.jpg")
	#files = glob.glob("../../image_compression/images/" + folder + "_Q50" + "/*.jpg")
	i = 0
	for f in files:
		i += 1
		os.system("jpegtran -optimize " + f + " temp_opt.jpg")
		size_opt += int(os.path.getsize("temp_opt.jpg"))
		os.system("jpegtran -optimize -progressive " + f + " temp_pro.jpg")
		size_pro += int(os.path.getsize("temp_pro.jpg"))
		os.system("jpegtran -arithmetic " + f + " temp_ari.jpg")
		size_ari += int(os.path.getsize("temp_ari.jpg"))
		
		commands.getstatusoutput("jpegtran -outputcoef opt_coef temp_opt.jpg temp")
		commands.getstatusoutput("jpegtran -outputcoef pro_coef temp_pro.jpg temp")
		#c = commands.getstatusoutput("diff opt_coef pro_coef")
		#if c[1] != '':
		#	print "problem!!"
		#	exit()
	x.append(int(folder))	
	opt_size.append(size_opt/100)
	pro_size.append(size_pro/100)
	ari_size.append(size_ari/100)
	diff_ratio_pro.append((size_opt - size_pro)*100.0/size_opt)
	diff_ratio_ari.append((size_opt - size_ari)*100.0/size_ari)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(x, opt_size, '-rd')
ax.plot(x, pro_size, '-yd')
ax.plot(x, ari_size, '-bd')
ax.set_xlabel("image type")
ax.set_ylabel("image size")
ax.legend(['optimized', 'progressive', 'arithmetic'], 3)
ax.grid()
ax2 = ax.twinx()
ax2.plot(x, diff_ratio_pro, 'k')
ax2.plot(x, diff_ratio_ari, 'k:')
ax2.set_ylabel("saving ratio (%)")
ax2.legend(['progressive', 'arithmetic'], 2)
ax.set_xlim([-500, 1200])
savefig("opt_pro_ari_75.png")
