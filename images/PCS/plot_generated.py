# this file is to plot PSNR / rate curve for different quality factor, and by zero-off of using different threshold
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, commands
import matplotlib.gridspec as gridspec
from pylab import *
import pickle, re

def get_pixels(f):
	c = commands.getstatusoutput("identify %s"%(f))
	s = c[1].split(" ")
	ss = s[2].split("x")
	return int(ss[0])*int(ss[1])


def get_threshold_jpg(out_, threshold, block_file, base_file):
	global folder
	c = commands.getstatusoutput("python ../../lossy_zerooff_ssim.py %s tmp_out.block__ %s %s"%(block_file, str(threshold), str(75)))
	print "(", c[1], 
	c = commands.getstatusoutput("/opt/libjpeg-turbo-coef/bin/jpegtran -inputcoef tmp_out.block__ %s temp3.jpg"%(base_file))
	c = commands.getstatusoutput("jpegtran -optimize temp3.jpg %s"%(out_))

#qs = ["bpp_0.25", "bpp_0.5", "bpp_0.75", "bpp_1", "bpp_1.25","bpp_1.5"]
qs = ["_0.25", "_0.5", "_0.75", "_1", "_1.25","_1.5"]

dest_bpp = [0.25, 0.5, 0.75, 1, 1.25, 1.5]
print qs

q_min = {}
q_max = {}

#ran = pickle.load(open("range.pcs"))
ran = pickle.load(open("range2_all.pcs"))

for d in dest_bpp:
	for f in glob.glob("./*.bmp"):
		s = f
		ind = s[s.find("/")+1:s.find("orig")+4]
		if not ind in q_min or ran[d][f][0]< q_min[ind]:
			q_min[ind] = ran[d][f][0]
		if not ind in q_max or ran[d][f][1]> q_max[ind]:
			q_max[ind] = ran[d][f][1]

print q_min
print q_max

root_folder = "psnr2_generated"
os.system("rm %s -rf"%(root_folder))
os.system("mkdir %s"%(root_folder))


for f in glob.glob("./*.bmp"):
	s = f
	ind = s[s.find("/")+1:s.find("orig")+4]
	print ind
	psnr_ = []
	ssim_ = []
	size_ = []
	raw_file = s[s.find("/")+1:s.find("orig")+4] + ".bmp"
	pix = get_pixels(ind+".bmp")
	p_ = {}
	s_ = {}
	si_ = {}
	for q in range(q_min[ind]-3, q_max[ind]+3):
		print q
		c = commands.getstatusoutput("convert -sampling-factor 4:2:0 -quality " + str(q)  + " "  + raw_file + " temp_9.jpg")
		c = commands.getstatusoutput("compare -metric PSNR " + raw_file + " temp_9.jpg tmp_diff_9.png")
		psnr_.append(float(c[1]))
		p_[q] = float(c[1])
		c = commands.getstatusoutput("pyssim "  + raw_file + " temp_9.jpg")
		ssim_.append(float(c[1]))
		s_[q] = float(c[1])
		size_.append(os.path.getsize("temp_9.jpg")*8.0/pix)
		si_[q] = os.path.getsize("temp_9.jpg")*8.0/pix

	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.plot(size_, psnr_, "--k")
	leg = ["from raw"]
	for q in qs:
		f_ = glob.glob("lromp2_bpp" + q + "/" + ind + "*.jpg")[0]
		psnr__ = []
		ssim__ = []
		size__ = []
		psnr__.append(float(commands.getstatusoutput("compare -metric PSNR " + raw_file + " " + f_ + " tmp_diff_9.png")[1]))
		ssim__.append(float(commands.getstatusoutput("pyssim " + raw_file + " " + f_)[1]))
		size__.append(os.path.getsize(f_)*8.0/pix)
		reg = re.match("(.*)/(.*)_q(.*)_t(.*)\.jpg\.jpg", f_)
		q_ = int(reg.group(3))
		psnr__.append(p_[q_])
		ssim__.append(s_[q_])
		size__.append(si_[q_])
		ax.plot(size__, psnr__, '-x')
		leg.append("q:"+str(q_) + " t:"+str(reg.group(4)))

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
		f_ = glob.glob("lromp2_bpp" + q + "/" + ind + "*.jpg")[0]
		psnr__ = []
		ssim__ = []
		size__ = []
		psnr__.append(float(commands.getstatusoutput("compare -metric PSNR " + raw_file + " " + f_ + " tmp_diff_9.png")[1]))
		ssim__.append(float(commands.getstatusoutput("pyssim " + raw_file + " " + f_)[1]))
		size__.append(os.path.getsize(f_)*8.0/pix)
		reg = re.match("(.*)/(.*)_q(.*)_t(.*)\.jpg\.jpg", f_)
		q_ = int(reg.group(3))
		psnr__.append(p_[q_])
		ssim__.append(s_[q_])
		size__.append(si_[q_])
		ax.plot(size__, ssim__, '-x')
		leg.append("q:"+str(q_) + " t:"+str(reg.group(4)))

	ax.set_xlabel("Bits-Per-Pixel")
	ax.grid()
	ax.set_ylabel("SSIM")
	ax.legend(leg, 4)
	tight_layout()
	savefig("%s/ssim_%s.png"%(root_folder, ind))
