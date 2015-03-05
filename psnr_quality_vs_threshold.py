# this file is to plot PSNR / rate curve for different quality factor, and by zero-off of using different threshold

import os, sys, glob, commands
import matplotlib.pyplot as plt
from pylab import *

def get_threshold_jpg(out_, threshold, block_file, base_file):
	global folder
	c = commands.getstatusoutput("python lossy_zerooff.py %s tmp_out.block %s"%(block_file, threshold))
	c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -inputcoef tmp_out.block %s %s"%(base_file, out_))

fs = glob.glob("images/TESTIMAGES/RGB/RGB_R02_0600x0600/*.png")
#fs = glob.glob("images/TESTIMAGES/RGB/RGB_OR_1200x1200/*.png")


qs = range(60, 91)
print qs
#qs = [30, 50, 70]

root_folder = "psnr_q_vs_t"
c = commands.getstatusoutput("rm %s -rf"%(root_folder))
c = commands.getstatusoutput("mkdir " + root_folder)

folder = ""
p_q_x = []
p_q_y = []
p_3_x = []
p_3_y = []
p_5_x = []
p_5_y = []
p_10_x = []
p_10_y = []
for q in qs:
	print ""
	print q
	folder = "%s/q_%s"%(root_folder, q)
	c = commands.getstatusoutput("rm %s -rf"%(folder))
	c = commands.getstatusoutput("mkdir %s"%(folder))

	x=0
	psnr1_ = 0.0
	delta = 0.0
	psnr_q = 0.0
	psnr_3 = 0.0
	psnr_5 = 0.0
	psnr_10 = 0.0
	size_q = 0
	size_3 = 0
	size_5 = 0
	size_10 = 0
	#fs = fs[0:20]
	for f in fs:
		x += 1
		#print " "
		print x,f,":","    ", 
		c = commands.getstatusoutput("convert -quality " + str(q)  + " "  + f + " " + folder + "/" + str(x) +".jpg")
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -outputcoef tmp.block %s %s"%(folder+"/"+str(x)+".jpg", folder+"/"+str(x)+"_std.jpg"))
		get_threshold_jpg(folder+"/"+str(x)+"_3.jpg", 3, "tmp.block", folder+"/"+str(x)+"_std.jpg")
		get_threshold_jpg(folder+"/"+str(x)+"_5.jpg", 5, "tmp.block", folder+"/"+str(x)+"_std.jpg")
		get_threshold_jpg(folder+"/"+str(x)+"_10.jpg", 10, "tmp.block", folder+"/"+str(x)+"_std.jpg")
		c = commands.getstatusoutput("compare -metric PSNR " + f + " %s/%s.jpg tmp_diff.png"%(folder, str(x)))
		print c[1], 
		psnr_q += float(c[1])
		c = commands.getstatusoutput("compare -metric PSNR " + f + " %s/%s_3.jpg tmp_diff.png"%(folder, str(x)))
		print c[1],
		psnr_3 += float(c[1])
		c = commands.getstatusoutput("compare -metric PSNR " + f + " %s/%s_5.jpg tmp_diff.png"%(folder, str(x)))
		print c[1],
		psnr_5 += float(c[1])
		c = commands.getstatusoutput("compare -metric PSNR " + f + " %s/%s_10.jpg tmp_diff.png"%(folder, str(x)))
		print c[1]
		psnr_10 += float(c[1])
		size_q += os.path.getsize("%s/%s_std.jpg"%(folder, str(x)))
		size_3 += os.path.getsize("%s/%s_3.jpg"%(folder, str(x)))
		size_5 += os.path.getsize("%s/%s_5.jpg"%(folder, str(x)))
		size_10 += os.path.getsize("%s/%s_10.jpg"%(folder, str(x)))
	
		
	psnr_q /= len(fs)
	psnr_3 /= len(fs)
	psnr_5 /= len(fs)
	psnr_10 /= len(fs)
	size_q /= len(fs)
	size_3 /= len(fs)
	size_5 /= len(fs)
	size_10 /= len(fs)
	p_q_x.append(size_q)
	p_3_x.append(size_3)
	p_5_x.append(size_5)
	p_10_x.append(size_10)
	p_q_y.append(psnr_q)
	p_3_y.append(psnr_3)
	p_5_y.append(psnr_5)
	p_10_y.append(psnr_10)

print p_q_x, p_q_y
print p_3_x, p_3_y
print p_5_x, p_5_y
print p_10_x, p_10_y
exit(0)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(p_q_x, p_q_y, '-x')
ax.plot(p_3_x, p_3_y, '-o')
ax.plot(p_5_x, p_5_y, '-s')
ax.plot(p_10_x, p_10_y, '-d')
ax.set_xlabel("file size (B)")
ax.grid()
ax.set_ylabel("PSNR (dB)")
ax.legend(['original','th=3', 'th=5', 'th=10'], 4)
savefig("psnr_quality_vs_threshold.png")
