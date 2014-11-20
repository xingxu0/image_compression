import sys, copy, os, heapq, glob, operator, pickle, lib, commands
from operator import itemgetter
import matplotlib.pyplot as plt
from pylab import *


folders = ['100', '200', '300', '400', '600', '800', '1000', '1200']

opt_size = []
pro_size = []
diff_ratio = []
for folder in folders:
	size_opt = 0
	size_pro = 0
	files = glob.glob("../../image_compression/images/" + folder + "_Q75" + "/*.jpg")
	i = 0
	for f in files:
		i += 1
		os.system("jpegtran -optimize " + f + " temp_opt.jpg")
		size_opt += int(os.path.getsize("temp_opt.jpg"))
		os.system("jpegtran -optimize -progressive " + f + " temp_pro.jpg")
		size_pro += int(os.path.getsize("temp_pro.jpg"))
		commands.getstatusoutput("jpegtran -outputcoef opt_coef temp_opt.jpg temp")
		commands.getstatusoutput("jpegtran -outputcoef pro_coef temp_pro.jpg temp")
		c = commands.getstatusoutput("diff opt_coef pro_coef")
		if c[1] != '':
			print "problem!!"
			exit()
		
	opt_size.append(size_opt/100)
	pro_size.append(size_pro/100)
	diff_ratio.append((size_opt - size_pro)*100.0/size_opt)
	
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(opt_size)
ax.plot(pro_size)
ax.set_xlabel("image type")
ax.set_ylabel("image size")
ax.set_xticklabels(folders)
ax.legend(['optimized', 'progressive'], 4)
ax2 = ax.twinx()
ax2.plot(diff_ratio, 'k')
ax2.set_ylabel("progressive saving ratio (%)")
ax2.legend(['progressive saving ratio'], 1)
savefig("progressive_vs_optimized.png")
		
