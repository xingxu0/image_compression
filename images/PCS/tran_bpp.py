import os, sys, glob, commands

def get_pixels(f):
	c = commands.getstatusoutput("identify %s"%(f))
	s = c[1].split(" ")
	ss = s[2].split("x")
	return int(ss[0])*int(ss[1])

dest_bpp = [0.25, 0.5, 0.75, 1, 1.25, 1.5]

fs = glob.glob("./*.bmp")

for b in dest_bpp:
	os.system("rm %s -rf"%("bpp_"+str(b)))
	os.system("mkdir %s"%("bpp_"+str(b)))
	for f in fs:
		fname = f[f.find("/")+1:f.find("bmp") - 1]
		print fname,
		ps = get_pixels(f)
		desired_size = ps*b/8
		print ps, "x", b, "=",desired_size
		last_q_size = -1
		for q in range(99, 0, -1):
			print q,
			os.system("convert -sampling-factor 4:2:0 -quality " + str(q)  + " "  + f + " temp.jpg")
			fz = os.path.getsize("temp.jpg")
			print "(", fz, ")",
			if fz < desired_size:
				if desired_size - fz < last_q_size - desired_size:
					print "[", q,"]"
					os.system("cp temp.jpg %s/%s"%("bpp_"+str(b), fname + "_q" + str(q)+".jpg" ))
				else:
					print "[", q+1,"]"
					os.system("cp temp2.jpg %s/%s"%("bpp_"+str(b), fname + "_q" + str(q+1)+".jpg" ))
				break
			else:
				last_q_size = fz
				os.system("cp temp.jpg temp2.jpg")
		print ""
