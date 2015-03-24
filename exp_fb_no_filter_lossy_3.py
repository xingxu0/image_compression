import os, commands, re, sys, time, glob

QP = 71
TRAIN_NUMBER = 10

def printf(f, s):
	f.write(s + "\n")
	print s

root = sys.argv[1]

commands.getstatusoutput("rm %s/train -rf"%(root))
commands.getstatusoutput("rm %s/test -rf"%(root))
commands.getstatusoutput("rm %s/table -rf"%(root))
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

os.system("python training_2_3_dc_zerooff.py %s/train %s/table 1 9 0.004"%(root, root))

#std,opt,ari,pro,moz = get_candidates_size("%s/test"%(root))

t_our = 0
t_std = 0
t_opt = 0
t_ari = 0
t_pro = 0
t_moz = 0
tfs = glob.glob("%s/test/*.jpg"%(root))
for f in tfs:
	c = commands.getstatusoutput("/opt/libjpeg-turbo-lossy/bin/jpegtran -encode %s/table 0.004 %s %s/temp.jpg"%(root, f, root))
	m = re.match("Total saving: (.*) bits\nOriginal filesize: (.*), encoded filesize: (.*), saving: (.*)\nTotal time elapsed : (.*) us", c[1])
	our = int(m.group(3))
	t_our += our

	c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -copy none %s %s/temp.jpg"%(f, root))
	std = os.path.getsize("%s/temp.jpg"%(root))
	t_std += std

	c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -copy none -optimize %s %s/temp.jpg"%(f, root))
	opt = os.path.getsize("%s/temp.jpg"%(root))
	t_opt += opt

	c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -copy none -arithmetic %s %s/temp.jpg"%(f, root))
	ari = os.path.getsize("%s/temp.jpg"%(root))
	t_ari += ari

	c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -copy none -progressive %s %s/temp.jpg"%(f, root))
	pro = os.path.getsize("%s/temp.jpg"%(root))
	t_pro += pro

	c = commands.getstatusoutput("time -p /opt/mozjpeg/bin/jpegtran -copy none %s > %s/temp.jpg"%(f, root))
	moz = os.path.getsize("%s/temp.jpg"%(root))
	t_moz += moz

	printf(f_out, "\t\t" +str(f) + ": our %d, std %d, opt %d, ari %d, pro %d, moz %d"%(our, std, opt, ari, pro, moz))
commands.getstatusoutput("rm %s/temp.jpg"%(root))
#printf(f_out, "\t" + str(total_std_size) + " " + str(total_encoded_size) + " " + str((total_std_size-total_encoded_size)*1.0/total_std_size))
printf(f_out, "our %d, std %d, opt %d, ari %d, pro %d, moz %d"%(t_our, t_std, t_opt, t_ari, t_pro, t_moz))
f_out.close()
