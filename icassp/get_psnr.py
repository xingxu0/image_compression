import os,sys,commands,glob

root = "webp"
os.system("mkdir " + root)
webp_bin = "/home/zahaib/libwebp-0.4.1-linux-x86-64/bin"

os.system("mkdir %s/q75"%(root))
i = 0
origin = {}
for f in glob.glob("/home/zahaib/ROMP/TESTIMAGES/RGB/RGB_OR_1200x1200/*.png"):
	i += 1
	os.system("convert -sampling-factor 4:2:0 -quality 75 %s %s/q75/%d.jpg"%(f, root, i))
	origin[i] = f

for q in range(50, 51):
	p = 0.0
	s = 0.0
	i = 0
	for i in range(1, 101):
		print i
		f = "%s/q75/%d.jpg"%(root, i)
		commands.getstatusoutput("%s/cwebp -q %d %s -o temp.webp"%(webp_bin , q, f))
		commands.getstatusoutput("%s/dwebp -bmp temp.webp -o temp.bmp"%(webp_bin))
		p += float(commands.getstatusoutput("compare -metric PSNR %s temp.bmp  temp_diff.png"%(origin[i]))[1])
		s += os.path.getsize("temp.webp")
	print q,":",p*1.0/i,s*1.0/i
