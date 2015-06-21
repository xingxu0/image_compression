import matplotlib
matplotlib.use('Agg')
import os, sys, glob, commands, pickle, operator, get_msssim, re
import matplotlib.pyplot as plt
from pylab import *



def get_pixels(f):
	c = commands.getstatusoutput("identify %s"%(f))
	s = c[1].split(" ")
	ss = s[2].split("x")
	return int(ss[0])*int(ss[1])

def get_threshold_jpg(out_, threshold, block_file, base_file):
	c = commands.getstatusoutput("python ../lossy_zerooff2.py %s ttttmp_out.block_ %s %s"%(block_file, str(threshold), str(75)))
	c = commands.getstatusoutput("/opt/libjpeg-turbo-coef/bin/jpegtran -inputcoef ttttmp_out.block_ %s tttttemp2.jpg"%(base_file))
	c = commands.getstatusoutput("jpegtran -optimize tttttemp2.jpg %s"%(out_))

image_folder = sys.argv[1]
out_folder = sys.argv[2]

fb_qp = 71

os.system("rm %s -rf"%(out_folder))
os.system("mkdir %s"%(out_folder))
os.system("mkdir %s/fb_%d"%(out_folder, fb_qp))

i = 0
s = 0
p = 0.0
size = {}
psnr = {}
ori_file_map = {}
for f in glob.glob(image_folder + "/*.png"):
	i += 1
	os.system("convert -sampling-factor 4:2:0 -quality %d %s temp.jpg"%(fb_qp, f))
	os.system("jpegtran -optimize temp.jpg %s/fb_%d/%d.jpg"%(out_folder, fb_qp, i))
	s += os.path.getsize("%s/fb_%d/%d.jpg"%(out_folder, fb_qp, i))
	p += float(commands.getstatusoutput("compare -metric PSNR temp.jpg " + f + " temp_diff.jpg")[1])
	ori_file_map[i] = f
size[0] = s/i
psnr[0] = p/i

thre = [1,2,3,4,5,6,7,8,9,12]
fs = glob.glob(out_folder + "/fb_%d/*.jpg"%(fb_qp))

for t in thre:
	print t 
	os.system("rm %s/thres_%d -rf"%(out_folder, t))
	os.system("mkdir %s/thres_%d"%(out_folder, t))
	s = 0
	p = 0.0
	for f in fs:
		print "", f
		ind = int(re.match("(.*)/(.*)\.jpg", f).group(2))
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -outputcoef temp.block " + f + " temp.base")
		get_threshold_jpg("%s/thres_%d/%d.jpg"%(out_folder, t, ind), t, "temp.block", "temp.base")
		s += os.path.getsize("%s/thres_%d/%d.jpg"%(out_folder, t, ind))
		p += float(commands.getstatusoutput("compare -metric PSNR " + "%s/thres_%d/%d.jpg "%(out_folder, t, ind) + ori_file_map[ind] + " temp_diff.jpg")[1])
	size[t] = s/len(fs)
	psnr[t] = p/len(fs)
	os.system("python exp_23dc_folder.py %s/thres_%d"%(out_folder, t))
print size
print psnr

fig = plt.figure()
ax = fig.add_subplot(111)

x1 = []
y1 = []
for x in [0] + thre:
	x1.append(size[x])
	y1.append(psnr[x])
ax.plot(x1, y1, "-bo")
ax.legend(["thre" + str(thre)], 4)
ax.set_xlabel("Size (B)")
ax.set_ylabel("PSNR")
tight_layout()
savefig("%s/plot.png"%(out_folder))
