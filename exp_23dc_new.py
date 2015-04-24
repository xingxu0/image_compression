import os, commands, re, sys, time
import matplotlib.pyplot as plt
from pylab import *

folders = ['50','55', '60','65', '70','75', '80','85', '90', '95']
folders = ['75']
#folders = ['95']


def printf(f, s):
	f.write(s + "\n")
	print s

def copy_images(folder, f, s, e):
	for i in range(1, 101):
		os.system("cp %s/%s.jpg %s/"%(f, str(i), folder))

def copy_other_images(folder, f, s, e):
	for i in range(1, 101):
		os.system("cp %s/%s.jpg %s/"%(f, str(i), folder))
			
def get_candidates_size(img_folder, q):
	total_std_size = 0
	total_opt_size = 0
	total_ari_size = 0
	total_pro_size = 0
	total_moz_size = 0
	total_pjg_size = 0

	for i in range(1, 101):
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -outputcoef t_opt " + img_folder + "/" + str(i) + ".jpg temp.jpg")
		total_std_size += os.path.getsize("temp.jpg")

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -optimize " + img_folder + "/" + str(i) + ".jpg temp.jpg")
		total_opt_size += os.path.getsize("temp.jpg")

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -arithmetic " + img_folder + "/" + str(i) + ".jpg temp.jpg")
		total_ari_size += os.path.getsize("temp.jpg")

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -progressive " + img_folder + "/" + str(i) + ".jpg temp.jpg")
		total_pro_size += os.path.getsize("temp.jpg")

		c = commands.getstatusoutput("time -p /opt/mozjpeg/bin/jpegtran " + img_folder + "/" + str(i) + ".jpg > temp.jpg")
		total_moz_size += os.path.getsize("temp.jpg")

		c = commands.getstatusoutput("./packJPG " + img_folder + "/" + str(i) + ".jpg")
		total_pjg_size += os.path.getsize(img_folder + "/" + str(i) + ".pjg")
		os.system("rm " + img_folder + "/" + str(i) + ".pjg")

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -outputcoef t_moz temp.jpg temp2.jpg")
		os.system("diff t_moz t_opt")

	return total_std_size, total_opt_size, total_ari_size, total_pro_size, total_moz_size, total_pjg_size
			
thre = float(sys.argv[1])

root = "post_exp_quality_" + str(int(time.time()))
os.system("mkdir %s"%(root))
f_out = open(root+"/exp.out", "w", 0)


for f in folders:
	printf(f_out, f)
	img_folder = "images/generate_1200x1200_%s"%(f)
	std,opt,ari,pro,moz,pjg = get_candidates_size(img_folder, f)
	overall_optimized_size = 0
	overall_encoded_size = 0
	if not (len(sys.argv) >= 2 and sys.argv[1]=="0"):
		for i in range(1):
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
			os.system("python training_2_3_dc.py %s/img_train %s/tbl_train"%(exp_folder, exp_folder))
			total_optimized_size = 0
			total_encoded_size = 0
			for j in range(1, 101):
				c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -encode %s/tbl_train %f %s/img_test/%s.jpg temp.jpg"%(exp_folder, thre, exp_folder, str(j)))
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
	printf(f_out, "\t our %d, std %d, opt %d, ari %d, pro %d, moz %d, pjg %d"%(overall_encoded_size, std, opt, ari, pro, moz, pjg))
f_out.close()
