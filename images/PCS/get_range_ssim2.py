import os, sys, glob, commands, pickle, operator

def get_pixels(f):
	c = commands.getstatusoutput("identify %s"%(f))
	s = c[1].split(" ")
	ss = s[2].split("x")
	return int(ss[0])*int(ss[1])

def get_threshold_jpg(out_, threshold, block_file, base_file):
	global folder
	c = commands.getstatusoutput("python ../../lossy_zerooff_ssim2.py %s tmp_out_ssim2.block %s %s"%(block_file, str(threshold), str(75)))
	c = commands.getstatusoutput("/opt/libjpeg-turbo-coef/bin/jpegtran -inputcoef tmp_out_ssim2.block %s temp_ssim2_range_.jpg"%(base_file))
	c = commands.getstatusoutput("jpegtran -optimize temp_ssim2_range_.jpg %s"%(out_))

dest_bpp = [0.25, 0.5, 0.75, 1, 1.25, 1.5]
#thre = [1,2,3,5,8,12]
thre = [5, 10, 50,100,200,300,500]

fs = glob.glob("./*.bmp")

#os.system("mkdir all_qp")
#for f in fs:
#	fname = f[f.find("/")+1:f.find("bmp") - 1]
#	for q in range(99, 0, -1):
#		os.system("convert -sampling-factor 4:2:0 -quality " + str(q)  + " "  + f + " all_qp/" + fname+"_q"+str(q)+".jpg")
#		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -outputcoef all_qp/" + fname+"_q"+str(q)+".block " + " all_qp/" + fname+"_q"+str(q)+".jpg " + " all_qp/" + fname+"_q"+str(q)+".base ")

if os.path.isfile("range2_ssim_all.pcs"):
	ran = pickle.load(open("range2_ssim_all.pcs"))
	print ran
else:
	ran = {}
	last_start_point = {}
	for f in fs:
		last_start_point[f] = 1
	for d in dest_bpp:
		print d
		ran[d] = {}
		for f in fs:
			print "\t", f
			ran[d][f] = {}
			fname = f[f.find("/")+1:f.find("bmp") - 1]
			ps = get_pixels(f)
			desired_size = ps*d/8
			min_ = -1
			max_ = -1
			flag = False
			done = False
			for q in range(last_start_point[f], 100):
				if done:
					break
				f_current = "all_qp/" + fname + "_q"+str(q)+".block"
				f_base = "all_qp/" + fname + "_q"+str(q)+".base"
				get_threshold_jpg("temp_ssim2_range.jpg", thre[len(thre)-1], f_current, f_base)
				fz = os.path.getsize("temp_ssim2_range.jpg")
				if not flag and fz > desired_size:
					print "\t\t", q, fz, desired_size
					min_ = q
					flag = True
				if flag:
					get_threshold_jpg("temp_ssim2_range.jpg", thre[0], f_current, f_base)
					fz = os.path.getsize("temp_ssim2_range.jpg")
					if fz > desired_size:
						done = True
						print "\t\t", q, fz, desired_size
					else:
						max_ = q
			ran[d][f][0] = min_
			last_start_point[f] = min_
			ran[d][f][1] = max_
	print ran
	pickle.dump(ran, open("range2_ssim_all.pcs", "wb"))
