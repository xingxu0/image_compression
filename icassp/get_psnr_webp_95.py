import os,sys,commands,glob

root = "webp_95"
os.system("mkdir " + root)
webp_bin = "/home/zahaib/libwebp-0.4.1-linux-x86-64/bin"

os.system("mkdir %s/q95"%(root))
i = 0
origin = {}
for f in glob.glob("/home/zahaib/ROMP/TESTIMAGES/RGB/RGB_OR_1200x1200/*.png"):
	i += 1
	os.system("convert -sampling-factor 4:2:0 -quality 95 %s %s/q95/%d.jpg"%(f, root, i))
	origin[i] = f

for q in range(1, 101):
	p = 0.0
	s = 0.0
	i = 0
	for i in range(1, 101):
		print i
		f = "%s/q95/%d.jpg"%(root, i)
		commands.getstatusoutput("%s/cwebp -q %d %s -o temp_webp.webp"%(webp_bin , q, f))
		commands.getstatusoutput("%s/dwebp -bmp temp_webp.webp -o temp_webp.bmp"%(webp_bin))
		p += float(commands.getstatusoutput("compare -metric PSNR %s temp_webp.bmp  temp_webp_diff.png"%(origin[i]))[1])
		s += os.path.getsize("temp_webp.webp")
	print q,":",p*1.0/i,s*1.0/i
