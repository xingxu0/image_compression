import os

root = "images/icassp_q75"

for i in range(1, 11):
	os.system("rm %s/2_%d -rf"%(root, i))
	os.system("cp %s/q75 %s/2_%d -rf"%(root, root, i))
	os.system("python exp_fb_lromp_ssim_local.py %s/2_%d 2.0 %f"%(root, i, i*1.0/10))
