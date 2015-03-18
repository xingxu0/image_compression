import os, commands, re, sys, time, glob

QP = 71
TRAIN_NUMBER = 1000

def get_quality(s):
	c = commands.getstatusoutput("identify -verbose %s | grep Quality"%(s))
	print c[1]
	if c[1].find("Quality:") == -1:
		return -1
	return int(c[1][c[1].find("Quality:") + 8:])

def filter_out(s):
	return
	for x in s:
		if get_quality(x) != QP:
			s.remove(x)
	
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
	for f in glob.glob("%s/*.jpg"%(img_folder)):
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -copy none %s %s/temp.jpg"%(f, img_folder))
		total_std_size += os.path.getsize("%s/temp.jpg"%(img_folder))

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -copy none -optimize %s %s/temp.jpg"%(f, img_folder))
		total_opt_size += os.path.getsize("%s/temp.jpg"%(img_folder))

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -copy none -arithmetic %s %s/temp.jpg"%(f, img_folder))
		total_ari_size += os.path.getsize("%s/temp.jpg"%(img_folder))

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -copy none -progressive %s %s/temp.jpg"%(f, img_folder))
		total_pro_size += os.path.getsize("%s/temp.jpg"%(img_folder))

		c = commands.getstatusoutput("time -p /opt/mozjpeg/bin/jpegtran -copy none %s > %s/temp.jpg"%(f, img_folder))
		total_moz_size += os.path.getsize("%s/temp.jpg"%(img_folder))
	commands.getstatusoutput("rm %s/temp.jpg"%(img_folder))
	return total_std_size, total_opt_size, total_ari_size, total_pro_size, total_moz_size

root = sys.argv[1]

commands.getstatusoutput("rm %s/train -rf"%(root))
commands.getstatusoutput("rm %s/test -rf"%(root))
commands.getstatusoutput("mkdir %s/train"%(root))
commands.getstatusoutput("mkdir %s/test"%(root))
f_out = open(root+"/exp.out", "w", 0)

fs = glob.glob("%s/*.jpg"%(root)) + glob.glob("%s/*.jpeg"%(root))
#filter_out(fs)
printf(f_out, "%d qualified images."%(len(fs)))

for i in range(min(TRAIN_NUMBER, len(fs))):
	commands.getstatusoutput("cp %s %s/train/"%(fs[i], root))
x = 1
for f in fs:
	commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -copy none %s %s/test/%d.jpg"%(f, root, x))
	x += 1

os.system("python training_2_3_dc.py %s/train %s/table"%(root, root))

std,opt,ari,pro,moz = get_candidates_size("%s/test"%(root))

total_std_size = 0
total_encoded_size = 0
tfs = glob.glob("%s/test/*.jpg"%(root))
for f in tfs:
	c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -encode %s/table %s %s/temp.jpg"%(root, f, root))
	m = re.match("Total saving: (.*) bits\nOriginal filesize: (.*), encoded filesize: (.*), saving: (.*)\nTotal time elapsed : (.*) us", c[1])
	jpg_std_size = int(m.group(2))
	out_size = int(m.group(3))
	saving_percent = float(m.group(4))
	total_encoded_size += out_size
	total_std_size += jpg_std_size
	printf(f_out, "\t\t" +str(f) + " : "+ str(saving_percent)) 
commands.getstatusoutput("rm %s/temp.jpg"%(root))
printf(f_out, "\t" + str(total_std_size) + " " + str(total_encoded_size) + " " + str((total_std_size-total_encoded_size)*1.0/total_std_size))
printf(f_out, "our %d, std %d, opt %d, ari %d, pro %d, moz %d"%(total_encoded_size, std, opt, ari, pro, moz))
f_out.close()
