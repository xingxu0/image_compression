import sys, copy, os, heapq, glob, operator, pickle, math
from operator import itemgetter
 
in_folder = sys.argv[1]
out_folder_1 = sys.argv[2]
out_folder_2 = sys.argv[3]

files = glob.glob(in_folder + "/*.block")

os.system("rm " + out_folder_1 + " -rf")
os.system("mkdir " + out_folder_1)
os.system("rm " + out_folder_2 + " -rf")
os.system("mkdir " + out_folder_2)

extra_bits = 0
for f in files:
	t_blocks = open(f).readlines()
	f1 = open(out_folder_1 + "/" + f[f.find("/")+1:], 'w')
	f2 = open(out_folder_2 + "/" + f[f.find("/")+1:], 'w')
	fe = open(out_folder_1 + "/" + f[f.find("/")+1:]+".extra", 'w')
	last_dc = 0
	for i in range(len(t_blocks)):
		s1 = ""
		s2 = ""
		s = t_blocks[i][:-2].split(" ")
		ii = []
		s1 += s[0]
		s2 += s[0]
		if s[0].find("0:") == -1:
			f1.write(t_blocks[i])
			continue
		for j in range(1, len(s)):
			if j==1:
				s1 += " " + s[j]
				s2 += " " + s[j]
			else:
				x = int(s[j])
				mo = 2
				s1 += " " + str(abs(x)/mo)				
				if abs(x) >= mo:
					if mo==2:
						extra_bits += math.log(mo, 2) + 1
						if x > 0:
							fe.write("1")
						else:
							fe.write("0")
						if (abs(x)%2) >0:
							fe.write("1")
						else:
							fe.write("0")
					s2 += " 0"
				else:
					s2 += " " + str(x)
		f1.write(s1 + " \n")
		f2.write(s2 + " \n")	
	f1.close()
	f2.close()
print extra_bits	



