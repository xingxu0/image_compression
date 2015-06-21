import os, commands, re, sys, time, glob
import matplotlib.pyplot as plt
from pylab import *

fb_qp = 71
save_thre = 0.2 # 20%

image_folder = sys.argv[1]
out_folder = sys.argv[2]

os.system("rm %s -rf"%(out_folder))
os.system("mkdir %s"%(out_folder))
os.system("mkdir %s/fb_%d"%(out_folder, fb_qp))

i = 0
s = 0
p = 0.0
size = {}
psnr = {}
size_raw = {}
psnr_raw = {}
ori_file_map = {}
for f in glob.glob(image_folder + "/*.png"):
	i += 1
	os.system("convert -sampling-factor 4:2:0 -quality %d %s temp.jpg"%(fb_qp, f))
	os.system("jpegtran -optimize temp.jpg %s/fb_%d/%d.jpg"%(out_folder, fb_qp, i))
	s += os.path.getsize("%s/fb_%d/%d.jpg"%(out_folder, fb_qp, i))
	p += float(commands.getstatusoutput("compare -metric PSNR temp.jpg " + f + " temp_diff.jpg")[1])
	ori_file_map[i] = f
size[fb_qp] = s/i
psnr[fb_qp] = p/i
size_raw[fb_qp] = s/i
psnr_raw[fb_qp] = p/i

now_qp = fb_qp - 1
saving = 0.0
while now_qp > 1 and saving < save_thre:
	os.system("mkdir %s/%d"%(out_folder, now_qp))
	i = 0
	s = 0
	p = 0.0
	for f in glob.glob("%s/fb_%d/*.jpg"%(out_folder, fb_qp)):
		ori = ori_file_map[int(re.match("(.*)/(.*)\.jpg", f).group(2))]
		i += 1
		os.system("convert -sampling-factor 4:2:0 -quality %d %s temp.jpg"%(now_qp, f))
		os.system("jpegtran -optimize temp.jpg %s/%d/%d.jpg"%(out_folder, now_qp, i))
		s += os.path.getsize("%s/%d/%d.jpg"%(out_folder, now_qp, i))
		p += float(commands.getstatusoutput("compare -metric PSNR temp.jpg " + ori + " temp_diff.jpg")[1])
	size[now_qp] = s/i
	psnr[now_qp] = p/i
	saving = (size[fb_qp] - size[now_qp])*1.0/size[fb_qp]

	s = 0
	p = 0.0
	i = 0
	for f in glob.glob(image_folder + "/*.png"):
		i += 1
		os.system("convert -sampling-factor 4:2:0 -quality %d %s temp.jpg"%(now_qp, f))
		s += os.path.getsize("temp.jpg")
		p += float(commands.getstatusoutput("compare -metric PSNR temp.jpg " + f + " temp_diff.jpg")[1])
	size_raw[now_qp] = s/i
	psnr_raw[now_qp] = p/i

	now_qp -= 1
final_qp = now_qp + 1
print "from 71"
print "", size
print "", psnr

print "from raw"
print "", size_raw
print "", psnr_raw


fig = plt.figure()
ax = fig.add_subplot(111)

x1 = []
y1 = []
for x in range(final_qp, fb_qp + 1):
	x1.append(size[x])
	y1.append(psnr[x])
ax.plot(x1, y1, "-bo")
x1 = []
y1 = []
for x in range(final_qp, fb_qp + 1):
	x1.append(size_raw[x])
	y1.append(psnr_raw[x])
ax.plot(x1, y1, "--k+")
ax.legend(["from %d"%(fb_qp), "from raw"], 4)
ax.set_xlabel("Size (B)")
ax.set_ylabel("PSNR")
tight_layout()
savefig("%s/plot.png"%(out_folder))
