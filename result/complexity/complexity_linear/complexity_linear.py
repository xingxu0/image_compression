import glob, os, sys, re, math, operator
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from pylab import *

def get_ratio(a, b):
	return (b-a)*1.0/b*100

folders = ['30','40','50','60','70','80','90']
folders = ['50','55','60','65','70','75','80','85','90','95']
folders = ['50','60','70','80','85','90','95']

our = {}
std = {}
opt = {}
ari = {}
pro = {}
moz = {}
pjg = {}
our[0] = []
our[1] = []
std[0] = []
std[1] = []
opt[0] = []
opt[1] = []
ari[0] = []
ari[1] = []
pro[0] = []
pro[1] = []
moz[0] = []
moz[1] = []
pjg[0] = []
pjg[1] = []

ls = open("complexity_packjpg_less.out").readlines()		

i = 0
print len(ls)
xx = []
while i < len(ls):
	l = ls[i]
	if l.find(",") != -1:
		t = l[:l.find(",")]
		print t
		t_size = int(t.split(" ")[1])
		xx.append(t_size*8.0/100/1200/1200)
	else:
		if l.find("Our:") != -1:
			now = our
			i += 1
			continue
		if l.find("Opt:") != -1:
			now = opt
			i += 1
			continue
		if l.find("Ari:") != -1:
			now = ari
			i += 1
			continue
		if l.find("Pro:") != -1:
			now = pro
			i += 1
			continue
		if l.find("Moz:") != -1:
			now = moz
			i += 1
			continue
		if l.find("Pjg:") != -1:
			i += 1
			now = pjg
			continue
		
		if l.find("(") != -1:
			if l.find("encoding") != -1:
				d = 0
			elif l.find("decoding") != -1:
				d = 1
			else:
				d = -1
			if d != -1:
				temp = l[l.find("(")+1:l.find(")")]
				temp2 = temp[:temp.find("ms")]
				time = float(temp2)
				now[d].append(time)
	i += 1

print our
print opt
print ari
print pro
print moz
print pjg
ress = ['320x240', '800x600', '1152x864', '1400x1050', '1600x1200', '2048x1536']
qs = ['50','55','60','65','70','75','80','90','95']

t_ress = []
for x in ress:
	t_ress.append(x[:x.find("x")])
xx = range(len(our[0]))
fig = plt.figure()
grid()
ax = fig.add_subplot(111)    # The big subplot
ax.plot(xx,our[0], "-x", ms=15)
ax.plot(xx,opt[0], "-o", ms=15)
ax.plot(xx,ari[0], "-d", ms=15)
ax.plot(xx,pro[0], "-s", ms=15)
ax.plot(xx,moz[0], "-p", ms=15)
ax.plot(xx,pjg[0], "-^", ms=15)
ax.set_ylim([0, 550])
#ax.set_xlim([-0.5, 6.5])
#ax.set_xlim([-0.5, 5.5])
ax.legend(["ROMP", "OPT", "ARI", "PRO", "MOZ", "PJG"], 2, fontsize=22, numpoints=1, ncol=3)
#ax.set_xlabel("Bits-Per-Pixel", fontsize=24)
ax.set_xlabel("Quality", fontsize=24)
plt.xticks(range(len(folders)), folders)#, rotation='30')
ax.set_ylabel("Time (ms)", fontsize=24)
plt.tick_params(axis='both', which='major', labelsize=22)
plt.tick_params(axis='both', which='minor', labelsize=22)
plt.tight_layout()
#fig.savefig("filesize.eps", bbox_inches='tight')
fig.savefig("complexity_enc.png", bbox_inches='tight')
fig.savefig("complexity_enc.eps", bbox_inches='tight')
#fig.savefig("fivek_quality.eps", bbox_inches='tight')

f = open("f_new_10_a.csv", "w")
i = 0
for q in folders:
	f.write(q+",")
	f.write(str(our[0][i])+",")
	f.write(str(opt[0][i])+",")
	f.write(str(ari[0][i])+",")
	f.write(str(pro[0][i])+",")
	f.write(str(moz[0][i])+",")
	f.write(str(pjg[0][i])+",")
	f.write("\n")
	i+=1
f.close()

f = open("f_new_10_b.csv", "w")
i = 0
for q in folders:
	f.write(q+",")
	f.write(str(our[1][i])+",")
	f.write(str(opt[1][i])+",")
	f.write(str(ari[1][i])+",")
	f.write(str(pro[1][i])+",")
	f.write(str(moz[1][i])+",")
	f.write(str(pjg[1][i])+",")
	f.write("\n")
	i+=1
f.close()


xx = range(len(our[0]))
fig = plt.figure()
grid()
ax = fig.add_subplot(111)    # The big subplot
ax.plot(xx,our[1], "-x", ms=15)
ax.plot(xx,opt[1], "-o", ms=15)
ax.plot(xx,ari[1], "-d", ms=15)
ax.plot(xx,pro[1], "-s", ms=15)
ax.plot(xx,moz[1], "-p", ms=15)
ax.plot(xx,pjg[1], "-^", ms=15)
ax.set_ylim([0, 550])
#ax.set_xlim([-0.5, 6.5])
#ax.set_xlim([-0.5, 5.5])
ax.legend(["ROMP", "OPT", "ARI", "PRO", "MOZ", "PJG"], 2, fontsize=22, numpoints=1, ncol=3)
#ax.set_xlabel("Bits-Per-Pixel", fontsize=24)
ax.set_xlabel("Quality", fontsize=24)
plt.xticks(range(len(folders)), folders)#, rotation='30')
ax.set_ylabel("Time (ms)", fontsize=24)
plt.tick_params(axis='both', which='major', labelsize=22)
plt.tick_params(axis='both', which='minor', labelsize=22)
plt.tight_layout()
#fig.savefig("filesize.eps", bbox_inches='tight')
fig.savefig("complexity_dec.png", bbox_inches='tight')
fig.savefig("complexity_dec.eps", bbox_inches='tight')
