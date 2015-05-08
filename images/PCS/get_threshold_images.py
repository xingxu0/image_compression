# this file is to plot PSNR / rate curve for different quality factor, and by zero-off of using different threshold
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, commands
import matplotlib.gridspec as gridspec
from pylab import *

def get_pixels(f):
	c = commands.getstatusoutput("identify %s"%(f))
	s = c[1].split(" ")
	ss = s[2].split("x")
	return int(ss[0])*int(ss[1])


def get_threshold_jpg(out_, threshold, block_file, base_file):
	global folder
	c = commands.getstatusoutput("python ../../lossy_zerooff.py %s tmp_out.block_ %s %s"%(block_file, str(threshold), str(75)))
	print "(", c[1], 
	c = commands.getstatusoutput("/opt/libjpeg-turbo-coef/bin/jpegtran -inputcoef tmp_out.block_ %s temp2.jpg"%(base_file))
	c = commands.getstatusoutput("jpegtran -optimize temp2.jpg %s"%(out_))

qs = ["bpp_0.25", ]#"bpp_0.5", "bpp_0.75", "bpp_1", "bpp_1.25", "bpp_1.5"]
print qs

#qs = [30, 50, 70]
#thre = [0,1.0/8/8/3,1.0/8/8/2,1.0/8/8,3.0/8/8] # 0 is for original (no thresholding)
thre = [0,1.0/18/18/8, 1.0/18/18/5, 1.0/18/18/3,1.0/18/18,3.0/18/18] # 0 is for original (no thresholding)
thre = [0, 0.012, 0.007, 0.003, 0.001]
#thre = [0,1.0/18/18/3,1.0/18/18,3.0/18/18, 5.0/18/18, 10.0/18/18] # 0 is for original (no thresholding)


print thre

root_folder = "psnr_q_vs_t"
c = commands.getstatusoutput("rm %s -rf"%(root_folder))
c = commands.getstatusoutput("mkdir " + root_folder)

folder = ""

psnr = {}
ssim = {}
size = {}
q_min = {}
q_max = {}
for f in glob.glob("./*.bmp"):
	s = f
	ind = s[s.find("/")+1:s.find("orig")+4]
	psnr[ind] = {}
	ssim[ind] = {}
	size[ind] = {}
	q_min[ind] = 100
	q_max[ind] = 0
	for q in qs:
		psnr[ind][q] = {}
		ssim[ind][q] = {}
		size[ind][q] = {}
		
		print q + "/" + ind + "*.jpg"
		f_q = glob.glob(q + "/" + ind + "*.jpg")[0]
		t = f_q
		q_ = int(t[t.find("_q")+2:t.find(".jpg")])
		if q_ < q_min[ind]:
			q_min[ind] = q_
		if q_ > q_max[ind]:
			q_max[ind] = q_

print q_min
print q_max

for q in qs:
	print ""
	print q
	folder = "%s/from_%s"%(root_folder, q)
	c = commands.getstatusoutput("rm %s -rf"%(folder))
	c = commands.getstatusoutput("mkdir %s"%(folder))

	fs = glob.glob("%s/*_orig*.jpg"%(q))
	for f in fs:
		s = f
		raw_file = s[s.find("/")+1:s.find("orig")+4] + ".bmp"
		ind = s[s.find("/")+1:s.find("orig")+4] 
		#print " "
		print ind,f,":","    " 
		#c = commands.getstatusoutput("convert -sampling-factor 4:2:0 -quality " + str(q)  + " "  + f + " " + folder + "/" + str(ind) +".jpg")
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -outputcoef tmp.block_ %s %s"%(f, folder+"/"+str(ind)+"_std.jpg"))
		c = commands.getstatusoutput("compare -metric PSNR " + raw_file + " " + f + " tmp_diff.png")
		print "[psnr ",c[1], "]",
		psnr[ind][q][0] = float(c[1])
		c = commands.getstatusoutput("pyssim "  + raw_file + " " + f)
		print "[ssim ", c[1],"]"
		ssim[ind][q][0] = float(c[1])
		size[ind][q][0] = os.path.getsize(f)
		for t in thre:
			if t:
				print t,
				get_threshold_jpg(folder+"/"+str(ind)+"_%f.jpg"%(t), t, "tmp.block_", folder+"/"+str(ind)+"_std.jpg")
				c = commands.getstatusoutput("compare -metric PSNR " + raw_file + " %s/%s_%f.jpg tmp_diff.png"%(folder, str(ind), t))
				print "psnr ", c[1], 
				psnr[ind][q][t] = float(c[1])
				c = commands.getstatusoutput("pyssim "  + raw_file + " %s/%s_%f.jpg"%(folder, str(ind), t))
				print "ssim ", c[1],")"
				ssim[ind][q][t] = float(c[1])
				size[ind][q][t] = os.path.getsize("%s/%s_%f.jpg"%(folder, str(ind), t))
		print ""

f_out = open(root_folder + "/index.out", "w")
for f in glob.glob("./*.bmp"):
	f_out.write(f + "\n")
	s = f
	ind = s[s.find("/")+1:s.find("orig")+4]
	psnr_ = []
	ssim_ = []
	size_ = []
	raw_file = s[s.find("/")+1:s.find("orig")+4] + ".bmp"
	pix = get_pixels(ind+".bmp")
	for q in range(q_min[ind]-3, q_max[ind]+4):
		c = commands.getstatusoutput("convert -sampling-factor 4:2:0 -quality " + str(q)  + " "  + raw_file + " temp.jpg")
		c = commands.getstatusoutput("compare -metric PSNR " + raw_file + " temp.jpg tmp_diff.png")
		psnr_.append(float(c[1]))
		c = commands.getstatusoutput("pyssim "  + raw_file + " temp.jpg")
		ssim_.append(float(c[1]))
		size_.append(os.path.getsize("temp.jpg")*8.0/pix)

	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.plot(size_, psnr_, "--k")
	leg = ["from raw"]
	for q in qs:
		x = []
		y = []
		for t in thre:
			x.append(size[ind][q][t]*8.0/pix)
			y.append(psnr[ind][q][t])
		ax.plot(x, y, '-x')
		leg.append(q)

	ax.set_xlabel("Bits-Per-Pixel")
	ax.grid()
	ax.set_ylabel("PSNR (dB)")
	ax.legend(leg, 4)
	tight_layout()
	savefig("%s/psnr_%s.png"%(root_folder, ind))

	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.plot(size_, ssim_, "--k")
	leg = ["from raw"]
	for q in qs:
		x = []
		y = []
		for t in thre:
			x.append(size[ind][q][t]*8.0/pix)
			y.append(ssim[ind][q][t])
		ax.plot(x, y, '-x')
		leg.append(q)

	ax.set_xlabel("Bits-Per-Pixel")
	ax.grid()
	ax.set_ylabel("SSIM")
	ax.legend(leg, 4)
	tight_layout()
	savefig("%s/ssim_%s.png"%(root_folder, ind))

	for q in qs:
		f_out.write("\t" + q + "\n")
		for t in thre:
			label = "starting JPEG"
			if t:
				label = str(t)

			o = size[ind][q][0]
			n = size[ind][q][t]
			saving = (o-n)*100/o
			f_out.write("\t\t" + label + ": " + str(n) + "(" + str(saving) + "%), ")

			o = psnr[ind][q][0]
			n = psnr[ind][q][t]
			saving = o-n
			f_out.write(str(n) + "(" + str(saving) + "), ")

			o = ssim[ind][q][0]
			n = ssim[ind][q][t]
			saving = o-n
			f_out.write(str(n) + "(" + str(saving) + ") ")
			if t:
				f_out.write("[ from_" + str(q) + "/" + str(ind) + "_%f.jpg"%(t) + "]\n")
			else:
				tt = glob.glob(str(q)+"/"+str(ind)+"*.jpg")[0]
				f_out.write("[ " + tt + "]\n")
		f_out.write("\n")
	f_out.write("\n")

f_out.close()

