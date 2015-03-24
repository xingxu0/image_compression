# this file is to plot PSNR / rate curve for different quality factor, and by zero-off of using different threshold
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, commands
import matplotlib.gridspec as gridspec
from pylab import *

def get_threshold_jpg(out_, threshold, block_file, base_file, quality):
	global folder
	c = commands.getstatusoutput("python lossy_zerooff_ssim.py %s tmp_out.block %s %s"%(block_file, str(threshold), str(quality)))
	print "(", c[1], 
	c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -inputcoef tmp_out.block %s %s"%(base_file, out_))

reso = "600"
fs = glob.glob("images/TESTIMAGES/RGB/RGB_R02_0600x0600/*.png")
#reso = "1200"
#fs = glob.glob("images/TESTIMAGES/RGB/RGB_OR_1200x1200/*.png")
fs = fs[:10]


qs = range(60, 91)
qs = [30,40,50,60,70,80,90]
qs = range(70, 96,5)
print qs
#qs = [30, 50, 70]
#thre = [0,1.0/8/8/3,1.0/8/8/2,1.0/8/8,3.0/8/8] # 0 is for original (no thresholding)
thre = [0,1.0/18/18,3.0/18/18, 5.0/18/18, 10.0/18/18,15.0/18/18] # 0 is for original (no thresholding)
#thre = [0, 3, 5, 10]


print thre

root_folder = "ssim_q_vs_t"
c = commands.getstatusoutput("rm %s -rf"%(root_folder))
c = commands.getstatusoutput("mkdir " + root_folder)

folder = ""

x = {}
y = {}
y2 = {}
s_r = {} # size reduction
for t in thre:
	x[t] = []
	y[t] = []
	y2[t] = []
	s_r[t] = []

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
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -outputcoef tmp.block %s %s"%(folder+"/"+str(ind)+".jpg", folder+"/"+str(ind)+"_std.jpg"))
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
				get_threshold_jpg(folder+"/"+str(ind)+"_%d.jpg"%(t), t, "tmp.block", folder+"/"+str(ind)+"_std.jpg", q)
				c = commands.getstatusoutput("compare -metric PSNR " + f + " %s/%s_%d.jpg tmp_diff.png"%(folder, str(ind), t))
				print "psnr ", c[1], 
				psnr[t] += float(c[1])
				c = commands.getstatusoutput("pyssim "  + f + " %s/%s_%d.jpg"%(folder, str(ind), t))
				print "ssim ", c[1],")",
				ssim[t] += float(c[1])
				size[t] += os.path.getsize("%s/%s_%d.jpg"%(folder, str(ind), t))
		print ""
	
	for t in thre:
		psnr[t] /= len(fs)
		size[t] /= len(fs)
		ssim[t] /= len(fs)
		s_r[t].append(100*(1-size[t]*1.0/size[0]))
		x[t].append(size[t])
		y[t].append(psnr[t])
		y2[t].append(ssim[t])
print x
print y
print y2
print s_r

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
savefig("S_psnr_quality_vs_threshold_%s.png"%(reso))
savefig("S_psnr_quality_vs_threshold_%s.eps"%(reso))

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
savefig("S_ssim_quality_vs_threshold_%s.png"%(reso))
savefig("S_ssim_quality_vs_threshold_%s.eps"%(reso))