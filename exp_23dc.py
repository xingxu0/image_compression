import os, commands, re, sys, time
import matplotlib.pyplot as plt
from pylab import *

folders = ['100', '200', '300', '400', '600', '800', '1000', '1200']

def printf(f, s):
	f.write(s + "\n")
	print s

def copy_images(folder, f, s, e):
	for i in range(s, e+1):
		os.system("cp %s/%s.jpg %s/"%(f, str(i), folder))

def copy_other_images(folder, f, s, e):
	for i in range(1, 101):
		if i < s or i > e:
			os.system("cp %s/%s.jpg %s/"%(f, str(i), folder))
			
def get_candidates_size(img_folder):
	total_std_size = 0
	total_opt_size = 0
	total_ari_size = 0
	total_pro_size = 0
	total_moz_size = 0

	for i in range(1, 101):
		os.system("/opt/libjpeg-turbo/bin/jpegtran -outputcoef t " + img_folder + "/" + str(i) + ".jpg temp.jpg")
		total_std_size += os.path.getsize("temp.jpg")

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -optimize " + img_folder + "/" + str(i) + ".jpg temp.jpg")
		total_opt_size += os.path.getsize("temp.jpg")

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -arithmetic " + img_folder + "/" + str(i) + ".jpg temp.jpg")
		total_ari_size += os.path.getsize("temp.jpg")

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -progressive " + img_folder + "/" + str(i) + ".jpg temp.jpg")
		total_pro_size += os.path.getsize("temp.jpg")

		c = commands.getstatusoutput("time -p /opt/mozjpeg/bin/jpegtran " + img_folder + "/" + str(i) + ".jpg > temp.jpg")
		total_moz_size += os.path.getsize("temp.jpg")
	return total_std_size, total_opt_size, total_ari_size, total_pro_size, total_moz_size

print "usage: python exp.py; python exp.py 0 if we don't want to calculate our size"

root = "exp_filesize_" + str(int(time.time()))
os.system("mkdir %s"%(root))
f_out = open(root+"/exp.out", "w", 0)


for f in folders:
	printf(f_out, f)
	img_folder = "images/%s_Q75"%(f)
	std,opt,ari,pro,moz = get_candidates_size(img_folder)
	overall_optimized_size = 0
	overall_encoded_size = 0
	if not (len(sys.argv) >= 2 and sys.argv[1]=="0"):
		for i in range(10):
			printf(f_out, "\t" + str(i))
			exp_folder = root+"/exp_" + f + "_" + str(i)
			os.system("rm %s -rf"%(exp_folder))
			os.system("mkdir %s"%(exp_folder))
			f_out_self = open(exp_folder+"/exp.out", "w", 0)
			os.system("mkdir %s/%s"%(exp_folder, "img_train"))
			copy_other_images("%s/%s"%(exp_folder, "img_train"), img_folder, i*10+1, i*10+10)
			os.system("mkdir %s/%s"%(exp_folder, "img_test"))
			copy_images("%s/%s"%(exp_folder, "img_test"), img_folder, i*10+1, i*10+10)
			if i > 0:
				os.system("cp %s/img_train/max* %s/img_train/"%(root+"/exp_" + f + "_0", exp_folder))
				os.system("cp %s/img_train/coef* %s/img_train/"%(root+"/exp_" + f + "_0", exp_folder))
			os.system("python training_2_3_dc.py %s/img_train %s/tbl_train 1 9"%(exp_folder, exp_folder))
			total_optimized_size = 0
			total_encoded_size = 0
			for j in range(i*10+1, i*10+10+1):
				c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -encode %s/tbl_train %s/img_test/%s.jpg temp.jpg"%(exp_folder, exp_folder, str(j)))
				printf(f_out, c[1])
				printf(f_out_self, c[1])
				m = re.match("Total saving: (.*) bits\nOriginal filesize: (.*), encoded filesize: (.*), saving: (.*)\nTotal time elapsed : (.*) us", c[1])
				jpg_opt_size = int(m.group(2))
				out_size = int(m.group(3))
				saving_percent = float(m.group(4))
				#encoding_time = int(m.group(5))
				total_optimized_size += jpg_opt_size
				total_encoded_size += out_size
			printf(f_out, "\t\t" + str(total_optimized_size) + " " + str(total_encoded_size) + " " + str((total_optimized_size-total_encoded_size)*1.0/total_optimized_size))
			printf(f_out_self, "\t\t" + str(total_optimized_size) + " " + str(total_encoded_size) + " " + str((total_optimized_size-total_encoded_size)*1.0/total_optimized_size))
			f_out_self.close()
			overall_optimized_size += total_optimized_size
			overall_encoded_size += total_encoded_size
		printf(f_out, "\t" + str(overall_optimized_size) + " " + str(overall_encoded_size) + " " + str((overall_optimized_size-overall_encoded_size)*1.0/overall_optimized_size))
	printf(f_out, "\t our %d, std %d, opt %d, ari %d, pro %d, moz %d"%(overall_encoded_size, std, opt, ari, pro, moz))
f_out.close()
