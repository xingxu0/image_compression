import os, commands, re, sys, time, glob
import matplotlib.pyplot as plt
from pylab import *

def get_size(ind, th):
	if ind == 0:
		a = 600
	else:
		a = 1200
	p_ = "our_%d_new/thres_%d/romp/exp.out"%(a, th)
	output = commands.getstatusoutput("grep \"our\" %s"%(p_))[1]
	size = int(re.match("\t our (.*), std(.*)", output).group(1))
	return size/100

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
	print now_qp
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

size_ = []
psnr_ = []
size_.append({0: 55247, 1: 39590, 2: 41976, 3: 46902, 4: 49516, 5: 51094, 6: 52302, 7: 52901, 8: 53566, 9: 54087, 12: 54960})
psnr_.append({0: 32.857589000000004, 1: 30.761366000000002, 2: 30.998739000000004, 3: 31.60859899999998, 4: 32.105168000000006, 5: 32.305609, 6: 32.46495999999999, 7: 32.56298799999998, 8: 32.648678000000004, 9: 32.708709000000006, 12: 32.82149299999999})

size_.append({0: 175369, 1: 123069, 2: 130728, 3: 146507, 4: 155465, 5: 160545, 6: 164633, 7: 167045, 8: 170036, 9: 172141, 12: 174844})
psnr_.append({0: 35.13110000000002, 1: 33.08652200000001, 2: 33.332389000000006, 3: 33.896048, 4: 34.40442000000001, 5: 34.575674999999976, 6: 34.73942599999999, 7: 34.85884499999999, 8: 34.95647000000001, 9: 35.016683999999984, 12: 35.107978})



thre = [1,2,3,4,5,6,7,8,9,12]
index = 0
if out_folder.find("600") != -1:
	index = 0
else:
	index = 1
x_romp = []
y_romp = []
x_lromp = []
y_lromp = []
print thre
for t in thre:
	si = get_size(index, t)
	y_romp.append(psnr_[index][t])
	x_romp.append(si)
	x_lromp.append(size_[index][t])
	y_lromp.append(psnr_[index][t])
	print t, ":"
	print "", si, str((size_[index][0]-si)*100.0/size_[index][0]) + "\%"
	print "", psnr_[index][t]


print x_romp
print y_romp
min_x = 10000000
max_x = -10000000
min_y = 100000000
max_y = -100000000
	
fig = plt.figure()
ax = fig.add_subplot(111)
x1 = []
y1 = []
for x in range(final_qp, fb_qp + 1):
	x1.append(size_raw[x])
	y1.append(psnr_raw[x])
ax.plot(x1, y1, "-k+")
min_x = min(min(x1), min_x)
max_x = max(max(x1), max_x)
min_y = min(min(y1), min_y)
max_y = max(max(y1), max_y)

x1 = []
y1 = []
for x in range(final_qp, fb_qp + 1):
	x1.append(size[x])
	y1.append(psnr[x])
ax.plot(x1, y1, "-b+")
min_x = min(min(x1), min_x)
max_x = max(max(x1), max_x)
min_y = min(min(y1), min_y)
max_y = max(max(y1), max_y)

ax.plot(x_lromp, y_lromp, "-rd")
ax.plot(x_romp, y_romp, "-ro")
min_x = min(min(x_romp), min_x)
max_x = max(max(x_romp), max_x)
min_y = min(min(y_romp), min_y)
max_y = max(max(y_romp), max_y)
min_x = min(min(x_lromp), min_x)
max_x = max(max(x_lromp), max_x)
min_y = min(min(y_lromp), min_y)
max_y = max(max(y_lromp), max_y)


#ax.legend(["from raw", "from %d"%(fb_qp), "L-ROMP %s"%(str(thre)), "ROMP %s"%(str(thre))], 4)
ax.legend(["from raw", "from %d"%(fb_qp), "L-ROMP", "ROMP"], 4)
for t in range(len(thre)):
	x_ = [x_romp[t], x_lromp[t]]
	y_ = [y_romp[t], y_lromp[t]]
	ax.plot(x_,y_, ":k", 0.05)
print min_x,max_x
print min_y,max_y
min_x -= (max_x-min_x)*0.05
max_x += (max_x-min_x)*0.05
min_y -= (max_y-min_y)*0.05
max_y += (max_y-min_y)*0.05


ax.set_xlim([min_x, max_x])
ax.set_ylim([min_y, max_y])

ax.set_xlabel("Size (B)")
ax.set_ylabel("PSNR")
tight_layout()
savefig("%s/plot.png"%(out_folder))
