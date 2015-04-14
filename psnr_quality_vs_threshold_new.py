# this file is to plot PSNR / rate curve for different quality factor, and by zero-off of using different threshold
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, commands
import matplotlib.gridspec as gridspec
from pylab import *

def get_threshold_jpg(out_, threshold, block_file, base_file, quality):
	global folder
	c = commands.getstatusoutput("python lossy_zerooff.py %s tmp_out.block_ %s %s"%(block_file, str(threshold), str(quality)))
	print "(", c[1], 
	c = commands.getstatusoutput("/opt/libjpeg-turbo-coef/bin/jpegtran -inputcoef tmp_out.block_ %s %s"%(base_file, out_))

#reso = "600"
fs = glob.glob("images/TESTIMAGES/RGB/RGB_R02_0600x0600/*.png")
reso = "1200"
fs = glob.glob("images/TESTIMAGES/RGB/RGB_OR_1200x1200/*.png")
fs = fs[:100]


qs = range(60, 91)
qs = [30,40,50,60,70,80,90]
qs = range(70, 95, 5)
qs = [55,60,65,70,75,80,85,90,95]
qs = [75]
print qs
#qs = [30, 50, 70]
#thre = [0,1.0/8/8/3,1.0/8/8/2,1.0/8/8,3.0/8/8] # 0 is for original (no thresholding)
thre = [0,1.0/18/18/8, 1.0/18/18/5, 1.0/18/18/3,1.0/18/18,3.0/18/18] # 0 is for original (no thresholding)
thre = [0, 0.001, 0.003, 0.007, 0.012]
#thre = [0,1.0/18/18/3,1.0/18/18,3.0/18/18, 5.0/18/18, 10.0/18/18] # 0 is for original (no thresholding)


print thre

root_folder = "psnr_q_vs_t"
c = commands.getstatusoutput("rm %s -rf"%(root_folder))
c = commands.getstatusoutput("mkdir " + root_folder)

folder = ""

x = {}
y = {}
y2 = {}
s_r = {} # size reduction
s_o = {} # size original
for t in thre:
	x[t] = []
	y[t] = []
	y2[t] = []
	s_r[t] = []
	s_o[t] = []

for q in qs:
	print ""
	print q
	folder = "%s/q_%s"%(root_folder, q)
	c = commands.getstatusoutput("rm %s -rf"%(folder))
	c = commands.getstatusoutput("mkdir %s"%(folder))

	ind=0
	psnr = {}
	ssim = {}
	size = {}
	for t in thre:
		psnr[t] = 0.0
		size[t] = 0
		ssim[t] = 0.0

	for f in fs:
		ind += 1
		#print " "
		print ind,f,":","    ", 
		c = commands.getstatusoutput("convert -sampling-factor 4:2:0 -quality " + str(q)  + " "  + f + " " + folder + "/" + str(ind) +".jpg")
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -outputcoef tmp.block_ %s %s"%(folder+"/"+str(ind)+".jpg", folder+"/"+str(ind)+"_std.jpg"))
		c = commands.getstatusoutput("compare -metric PSNR " + f + " %s/%s.jpg tmp_diff.png"%(folder, str(ind)))
		print "[psnr ",c[1], "]",
		psnr[0] += float(c[1])
		c = commands.getstatusoutput("pyssim "  + f + " %s/%s.jpg"%(folder, str(ind)))
		print "[ssim ", c[1],"]"
		ssim[0] += float(c[1])
		size[0] += os.path.getsize("%s/%s_std.jpg"%(folder, str(ind)))
		for t in thre:
			if t:
				print t
				get_threshold_jpg(folder+"/"+str(ind)+"_%f.jpg"%(t), t, "tmp.block_", folder+"/"+str(ind)+"_std.jpg", q)
				c = commands.getstatusoutput("compare -metric PSNR " + f + " %s/%s_%f.jpg tmp_diff.png"%(folder, str(ind), t))
				print "psnr ", c[1], 
				psnr[t] += float(c[1])
				c = commands.getstatusoutput("pyssim "  + f + " %s/%s_%f.jpg"%(folder, str(ind), t))
				print "ssim ", c[1],")",
				ssim[t] += float(c[1])
				size[t] += os.path.getsize("%s/%s_%f.jpg"%(folder, str(ind), t))
		print ""
	
	for t in thre:
		psnr[t] /= len(fs)
		size[t] /= len(fs)
		ssim[t] /= len(fs)
		s_r[t].append(100*(1-size[t]*1.0/size[0]))
		s_o[t].append(size[0])
		x[t].append(size[t])
		y[t].append(psnr[t])
		y2[t].append(ssim[t])
print x
print y
print y2
print s_r

print "#",
for q in qs:
	print q,
print ""

for t in thre:
	print t
	print "image size,",
	for tt in x[t]:
		print tt,",",
	print ""
	print "psnr,",
	for tt in y[t]:
		print tt,",",
	print ""
	print "ssim,",
	for tt in y2[t]:
		print tt,",",
	print ""
	print "original_size,",
	for tt in s_o[t]:
		print tt,",",
	print ""
	print "size reduction,",
	for tt in s_o[t]:
		print tt,",",
	print ""



fig = plt.figure()
gs = gridspec.GridSpec(2,1,height_ratios=[2,1])
ax = plt.subplot(gs[0])
#ax2 = fig.add_subplot(212)
ax2 = plt.subplot(gs[1])
leg = []
for t in thre:
	ax.plot(x[t], y[t], '-x')
	ax2.plot(qs, s_r[t], '-o')
	if t:
		leg.append("th=" + "%.5f"%(t))
	else:
		leg.append("original")
ax.set_xlabel("file size (B)")
ax.grid()
ax.set_ylabel("PSNR (dB)")
ax.legend(leg, 4)
#ax2.legend(leg, 4)
ax2.grid()
ax2.set_xlabel("Q")
ax2.set_ylabel("Bits Saving (%)")
ax2.set_xlim([min(qs)-3, max(qs)+3])
tight_layout()
savefig("Q_psnr_quality_vs_threshold_%s.png"%(reso))
savefig("Q_psnr_quality_vs_threshold_%s.eps"%(reso))

fig = plt.figure()
gs = gridspec.GridSpec(2,1,height_ratios=[2,1])
ax = plt.subplot(gs[0])
#ax2 = fig.add_subplot(212)
ax2 = plt.subplot(gs[1])
leg = []
for t in thre:
	ax.plot(x[t], y2[t], '-x')
	ax2.plot(qs, s_r[t], '-o')
	if t:
		leg.append("th=" + "%.5f"%(t))
	else:
		leg.append("original")
ax.set_xlabel("file size (B)")
ax.grid()
ax.set_ylabel("SSIM")
ax.legend(leg, 4)
#ax2.legend(leg, 4)
ax2.grid()
ax2.set_xlabel("Q")
ax2.set_ylabel("Bits Saving (%)")
ax2.set_xlim([min(qs)-3, max(qs)+3])
tight_layout()
savefig("Q_ssim_quality_vs_threshold_%s.png"%(reso))
savefig("Q_ssim_quality_vs_threshold_%s.eps"%(reso))
