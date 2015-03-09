#psnr  1
import os, sys, glob, commands

fs = glob.glob("images/TESTIMAGES/RGB/RGB_OR_1200x1200/*.png")

thre = sys.argv[1]

q = "75"
folder = "psnr_1200_q75_" + thre
c = commands.getstatusoutput("rm %s -rf"%(folder))
c = commands.getstatusoutput("mkdir " + folder)
x=0
psnr1_ = 0.0
delta = 0.0
for f in fs:
	x += 1
	print " "
	print x,":","    ", 
	c = commands.getstatusoutput("convert -quality " + q  + " "  + f + " " + folder + "/" + str(x) +".jpg")
	c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -outputcoef temp.block %s/%s.jpg temp.jpg"%(folder, str(x)))
	c = commands.getstatusoutput("python lossy_zerooff.py temp.block temp_out.block " + thre)
	c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -inputcoef temp_out.block temp.jpg %s/%s_zerooff.jpg"%(folder, str(x)))
	c = commands.getstatusoutput("compare -metric PSNR " + f + " %s/%s.jpg temp_diff.png"%(folder, str(x)))
	print c[1], 
	psnr1 = float(c[1])
	c = commands.getstatusoutput("compare -metric PSNR " + f + " %s/%s_zerooff.jpg temp_diff.png"%(folder, str(x)))
	print c[1]
	psnr2 = float(c[1])
	delta += psnr1-psnr2
	psnr1_ += psnr1
print psnr1_, psnr1_/x
print delta, delta/x

