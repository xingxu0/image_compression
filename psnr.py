import os, sys, glob

fs = glob.glob("images/TESTIMAGES/RGB/RGB_R02_0600x0600/*.png")

thre = sys.argv[1]

q = "75"
os.system("mkdir psnr_600_q75")
for f in fs:
	x += 1	
	cmd = "convert -quality " + q  + " "  + f + " psnr_600_q75/" + str(x) +".jpg"
	os.system("/opt/libjpeg-turbo/bin/jpegtran -outputcoef temp.block psnr_600_q75/%s.jpg temp.jpg"%(str(x)))
	os.system("python lossy_zerooff.py temp.block temp_out.block " + thre)
	os.system("/opt/libjpeg-turbo/bin/jpegtran -inputcoef temp_out.block temp.jpg psnr_600_q75/%s_zerooff.jpg"%(str(x)))
	os.system("compare -metric PSNR " + f + " psnr_600_q75/%s.jpg temp_diff.png"%(str(x)))
	os.system("compare -metric PSNR " + f + " psnr_600_q75/%s_zerooff.jpg temp_diff.png"%(str(x)))
