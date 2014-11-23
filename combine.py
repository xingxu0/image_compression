import sys, copy, os, heapq, glob, operator, pickle
from operator import itemgetter
 
in_folder = sys.argv[1]
out_folder_1 = sys.argv[2]
out_folder_2 = sys.argv[3]

files = glob.glob(in_folder + "/*.block")

os.system("rm temp -rf")
os.system("mkdir temp")
for f in files:
	t_blocks = open(f).readlines()
	f1 = open(out_folder_1 + "/" + f[f.find("/")+1:]).readlines()
	f2 = open(out_folder_2 + "/" + f[f.find("/")+1:]).readlines()
	fe = open(out_folder_1 + "/" + f[f.find("/")+1:]+".extra").readlines()[0]
	now = 0
	f_out = open("temp/"  + f[f.find("/")+1:], "w")
	last_dc = 0
	for i in range(len(t_blocks)):
		s1 = f1[i][:-2].split(" ")
		s2 = f2[i][:-2].split(" ")
		ii = []
		if s1[0] != s2[0]:
			print "error at 0"
		s = s1[0]
		for j in range(1, len(s1)):
			if j==1:
				if s1[1] != s2[1]:
					print "error at 1"
				s += " " + s1[1]
			else:
				if s1[0].find("0:")!=-1:
					mo = 4
				else:
					mo = 2

				x1 = int(s1[j])
				x2 = int(s2[j])
				if x1 != 0:
					if mo == 4:
						extra = fe[now:now+3]
						now+=3
						neg = False
						d = 0
						if extra[0] == "0":
							neg = True
						if extra[1] == "1":
							d+=2
						if extra[2] == "1":
							d+=1
						d += x1*4
						if neg:
							d = -d
						s += " " + str(d)
					else:
						extra = fe[now:now+2]
						now+=2
						neg = False
						d = 0
						if extra[0] == "0":
							neg = True
						if extra[1] == "1":
							d+=1
						d += x1*2
						if neg:
							d = -d
						s += " " + str(d)
				else:
					s += " " + str(x2)
		f_out.write(s + " \n")
	f_out.close()
print "check..."
for f in files:
	os.system("diff " + f + " temp/" + f[f.find("/")+1:])



