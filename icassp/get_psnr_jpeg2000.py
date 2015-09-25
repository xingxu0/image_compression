import os,sys,commands,glob

root = "jp2"
os.system("mkdir " + root)
webp_bin = "/home/zahaib/libwebp-0.4.1-linux-x86-64/bin"

os.system("mkdir %s/q75"%(root))
i = 0
origin = {}
for f in glob.glob("/home/zahaib/ROMP/TESTIMAGES/RGB/RGB_OR_1200x1200/*.png"):
	i += 1
	os.system("convert -sampling-factor 4:2:0 -quality 75 %s %s/q75/%d.jpg"%(f, root, i))
	origin[i] = f

for q in range(1, 101):
	p = 0.0
	s = 0.0
	i = 0
	for i in range(1, 101):
		print i
		f = "%s/q75/%d.jpg"%(root, i)
		#commands.getstatusoutput("%s/cwebp -q %d %s -o temp.webp"%(webp_bin , q, f))
		#commands.getstatusoutput("%s/dwebp -bmp temp.webp -o temp.bmp"%(webp_bin))
		c = commands.getstatusoutput("convert -limit thread 1 -quality %d %s temp.jp2"%(q, f))
		c = commands.getstatusoutput("convert -limit thread 1 temp.jp2 temp2.bmp")

		p += float(commands.getstatusoutput("compare -metric PSNR %s temp2.bmp temp_diff2.png"%(origin[i]))[1])
		s += os.path.getsize("temp.jp2")
	print q,":",p*1.0/i,s*1.0/i
