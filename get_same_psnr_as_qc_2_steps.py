# this file is to plot PSNR / rate curve for different quality factor, and by zero-off of using different threshold
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, commands
import matplotlib.gridspec as gridspec
from pylab import *

def get_threshold_jpg(out_, threshold, block_file, base_file, quality):
	global folder, qs
	c = commands.getstatusoutput("python lossy_zerooff.py %s tmp_out.block_%d %s %s"%(block_file, qs[0][1], str(threshold), str(quality)))
	cc = commands.getstatusoutput("/opt/libjpeg-turbo-coef/bin/jpegtran -inputcoef tmp_out.block_%d %s tmp_out.block__%d"%(qs[0][1], base_file, qs[0][1]))
	ccc = commands.getstatusoutput("jpegtran -optimize tmp_out.block__%d %s"%(qs[0][1], out_))
	cccc = commands.getstatusoutput("rm tmp_out.block__%d"%(qs[0][1]))
	return c[1]

#reso = "600"
fs = glob.glob("images/TESTIMAGES/RGB/RGB_R02_0600x0600/*.png")
reso = "1200"
fs = glob.glob("images/TESTIMAGES/RGB/RGB_OR_1200x1200/*.png")
fs = fs[:101]
#fs = fs[:11]



qs = []
qs.append((int(sys.argv[1]), int(sys.argv[2])))
qe = 80
print qs, qe
#qs = [30, 50, 70]
#thre = [0,1.0/8/8/3,1.0/8/8/2,1.0/8/8,3.0/8/8] # 0 is for original (no thresholding)
thre = [0,1.0/18/18/8, 1.0/18/18/5, 1.0/18/18/3,1.0/18/18,3.0/18/18] # 0 is for original (no thresholding)
thre = [-1, 0, 0.0016,0.0017,0.0018]#0.002,0.003,0.005]#,0.007, 0.01,0.015,0.02, 0.05, 0.07]#15]#005, 0.0001, 0.0005]#, 0.0009, 0.001, 0.0015]#, 0.007, 0.012]
#thre = [0,1.0/18/18/3,1.0/18/18,3.0/18/18, 5.0/18/18, 10.0/18/18] # 0 is for original (no thresholding)


print thre

root_folder = "lromp_to_80_vs_qc_%d"%(qs[0][1])
c = commands.getstatusoutput("rm %s -rf"%(root_folder))
c = commands.getstatusoutput("mkdir " + root_folder)

folder = ""

x = {}
y = {}
s_r = {} # size reduction
s_o = {} # size original
for t in thre:
	x[t] = []
	y[t] = []
	s_r[t] = []
	s_o[t] = []

for q in qs:
	print ""
	print q
	folder = "%s/q_uploaded_%d_%d"%(root_folder, q[0], q[1])
	folder_qc = "%s/q_qc_%s"%(root_folder, qe)
	c = commands.getstatusoutput("rm %s -rf"%(folder))
	c = commands.getstatusoutput("mkdir %s"%(folder))
	c = commands.getstatusoutput("rm %s -rf"%(folder_qc))
	c = commands.getstatusoutput("mkdir %s"%(folder_qc))


	ind=0
	psnr = {}
	size = {}
	for t in thre:
		psnr[t] = 0.0
		size[t] = 0
		if t>0:
			folder_ = "%s/q_lromp_%s"%(root_folder, int(t*10000))
			c = commands.getstatusoutput("rm %s -rf"%(folder_))
			c = commands.getstatusoutput("mkdir %s"%(folder_))

	for f in fs:
		ind += 1
		#print " "
		print ind,f,":","    ", 
		# ttt.jpg is q95 image
		c = commands.getstatusoutput("convert -sampling-factor 4:2:0 -quality " + str(q[0])  + " "  + f + " " + folder + "/ttt.jpg")
		# folder / ind.jpg is from q95 to q77
		c = commands.getstatusoutput("convert -sampling-factor 4:2:0 -quality " + str(q[1])  + " "  + folder+"/ttt.jpg" + " " + folder + "/" + str(ind) +".jpg")

		#c = commands.getstatusoutput("jpegtran -optimize %s %s; rm %s"%(folder + "/" + str(ind) +"_.jpg", folder + "/" + str(ind) +".jpg", folder + "/" + str(ind) +"_.jpg"))	
		# folder_qc / ind.jpg is from q95 to q75
		c = commands.getstatusoutput("convert -define jpeg:optimize-coding=on -sampling-factor 4:2:0 -quality " + str(qe)  + " " + folder + "/ttt.jpg " + folder_qc+"/"+str(ind)+".jpg")
		#c = commands.getstatusoutput("jpegtran -optimize %s %s; rm %s"%(folder_qc + "/" + str(ind) +"_.jpg", folder_qc + "/" + str(ind) +".jpg", folder_qc + "/" + str(ind) +"_.jpg"))	

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -outputcoef tmp.block_%d %s %s"%(qs[0][1], folder+"/"+str(ind)+".jpg", folder+"/"+str(ind)+"_std.jpg"))
		c = commands.getstatusoutput("compare -metric PSNR " + f + " %s/%s.jpg tmp_diff.png"%(folder, str(ind)))
		print "[psnr ", q, c[1], "]",
		psnr[-1] += float(c[1])
		size[-1] += os.path.getsize("%s/%s.jpg"%(folder, str(ind)))

		c = commands.getstatusoutput("compare -metric PSNR " + f + " %s/%s.jpg tmp_diff.png"%(folder_qc, str(ind)))
		print "[psnr ", q, "->", qe, c[1], "]",
		psnr[0] += float(c[1])
		#c = commands.getstatusoutput("pyssim "  + f + " %s/%s.jpg"%(folder, str(ind)))
		#print "[ssim ", c[1],"]"
		#ssim[0] += float(c[1])
		size[0] += os.path.getsize("%s/%s.jpg"%(folder_qc, str(ind)))
		for t in thre:
			if t>0:
				folder_ = "%s/q_lromp_%s"%(root_folder, int(t*10000))
				t_ = get_threshold_jpg(folder_+"/"+str(ind)+".jpg", t, "tmp.block_"+str(qs[0][1]), folder+"/"+str(ind)+".jpg", q[1])
				c = commands.getstatusoutput("compare -metric PSNR " + f + " %s/%s.jpg tmp_diff.png"%(folder_, str(ind)))
				print "[", t, ": psnr ", c[1], "(", t_, ")]",
				psnr[t] += float(c[1])
				#c = commands.getstatusoutput("pyssim "  + f + " %s/%s_%f.jpg"%(folder, str(ind), t))
				#print "ssim ", c[1],")",
				#ssim[t] += float(c[1])
				size[t] += os.path.getsize("%s/%s.jpg"%(folder_, str(ind)))
		print ""
	
	for t in thre:
		psnr[t] /= len(fs)
		size[t] /= len(fs)
		s_r[t].append(100*(1-size[t]*1.0/size[-1]))
		s_o[t].append(size[-1])
		x[t].append(size[t])
		y[t].append(psnr[t])
print t
print x
print y
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
	print "original_size,",
	for tt in s_o[t]:
		print tt,",",
	print ""
	print "size reduction,",
	for tt in s_r[t]:
		print tt,",",
	print ""
