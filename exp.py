import os, commands, re, sys
import matplotlib.pyplot as plt
from pylab import *

folders = ['100', '200', '300', '400', '600', '800', '1000', '1200']
folders = ['1200']
#folders = ['1200']

def printf(f, s):
	f.write(s + "\n")
	print s

def copy_images(folder, f, s, e):
	for i in range(s, e+1):
		os.system("cp images/%s_Q75/%s.jpg %s/"%(f, str(i), folder))

def copy_other_images(folder, f, s, e):
	for i in range(1, 101):
		if i < s or i > e:
			os.system("cp images/%s_Q75/%s.jpg %s/"%(f, str(i), folder))

f_out = open("exp.out", "w")

for f in folders:
	print f
	for i in range(10):
		printf(f_out, "\t" + str(i))
		exp_folder = "exp_" + f + "_" + str(i)
		os.system("rm %s -rf"%(exp_folder))
		os.system("mkdir %s"%(exp_folder))
		os.system("mkdir %s/%s"%(exp_folder, "img_train"))
		copy_other_images("%s/%s"%(exp_folder, "img_train"), f, i*10+1, i*10+10)
		os.system("mkdir %s/%s"%(exp_folder, "img_test"))
		copy_images("%s/%s"%(exp_folder, "img_test"), f, i*10+1, i*10+10)
		os.system("python training_all.py %s/img_train %s/tbl_train 1 12"%(exp_folder, exp_folder))
		total_optimized_size = 0
		total_encoded_size = 0
		for j in range(i*10+1, i*10+10+1):
			c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -encode %s/tbl_train %s/img_test/%s.jpg temp.jpg"%(exp_folder, exp_folder, str(j)))
			printf(f_out, c[1])
			m = re.match("Total saving: (.*) bits\nOriginal filesize: (.*), encoded filesize: (.*), saving: (.*)\nTotal time elapsed : (.*) us", c[1])
			jpg_opt_size = int(m.group(2))
			out_size = int(m.group(3))
			saving_percent = float(m.group(4))
			#encoding_time = int(m.group(5))
			total_optimized_size += jpg_opt_size
			total_encoded_size += out_size
		printf(f_out, "\t\t" + str(total_optimized_size) + " " + str(total_encoded_size) + " " + str((total_optimized_size-total_encoded_size)*1.0/total_optimized_size))
f_out.close()
