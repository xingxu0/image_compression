import os, commands, re, sys, time
import matplotlib.pyplot as plt
from pylab import *

folders = ['30', '40', '50', '60', '70', '80', '90', '100']

folders = ['80', '90', '100']


def printf(f, s):
	f.write(s + "\n")
	print s

def copy_images(folder, f, s, e):
	for i in range(s, e+1):
		os.system("cp images/generate_1200x1200_%s/%s.jpg %s/"%(f, str(i), folder))

def copy_other_images(folder, f, s, e):
	for i in range(1, 101):
		if i < s or i > e:
			os.system("cp images/generate_1200x1200_%s/%s.jpg %s/"%(f, str(i), folder))

root = "exp_" + str(int(time.time()))
os.system("mkdir %s"%(root))
f_out = open(root+"/exp.out", "w", 0)


for f in folders:
	print f
	overall_optimized_size = 0
	overall_encoded_size = 0
	for i in range(10):
		printf(f_out, "\t" + str(i))
		exp_folder = root+"/exp_" + f + "_" + str(i)
		os.system("rm %s -rf"%(exp_folder))
		os.system("mkdir %s"%(exp_folder))
		f_out_self = open(exp_folder+"/exp.out", "w", 0)
		os.system("mkdir %s/%s"%(exp_folder, "img_train"))
		copy_other_images("%s/%s"%(exp_folder, "img_train"), f, i*10+1, i*10+10)
		os.system("mkdir %s/%s"%(exp_folder, "img_test"))
		copy_images("%s/%s"%(exp_folder, "img_test"), f, i*10+1, i*10+10)
		if i > 1000:
			os.system("cp %s/img_train/max* %s/img_train/"%(root+"/exp_" + f + "_0", exp_folder))
			os.system("cp %s/img_train/coef* %s/img_train/"%(root+"/exp_" + f + "_0", exp_folder))
		os.system("python training_2_3_dc.py %s/img_train %s/tbl_train 1 12"%(exp_folder, exp_folder))
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
f_out.close()
