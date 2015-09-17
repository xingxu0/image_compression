import os

folder = []
#for i in range(50, 100, 5):
for i in range(200, 1400, 200):
	folder.append(i)
print folder
#exit()

for f in folder:
	os.system("echo %d >> add_lromp_size.out"%(f))
	os.system("python exp_fb_lromp_ssim.py images/generate_%d_75 2.0 0.4 >> add_lromp_size.out"%(f))

