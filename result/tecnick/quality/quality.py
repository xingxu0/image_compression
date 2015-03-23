import glob, os, sys, re, math, operator
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from pylab import *

def get_ratio(a, b):
	return (b-a)*1.0/b*100

folders = ['30','40','50','60','70','80','90']
folders = ['50','55','60','65','70','75','80','90','95']

our = []
std = []
opt = []
ari = []
pro = []
moz = []
pjg = []

ls = open("exp.out").readlines()
now_f = 0
i = 0
while i < len(ls) and now_f < len(folders):
	l = ls[i]
	if l.find(folders[now_f]) != 0:
		i += 1
		continue
	
	while i < len(ls):
		l = ls[i]
		if l.find("our") == -1:
			i += 1
			continue
		# our 297330, std 346633, opt 314927, ari 287861, pro 329301, moz 314797
		m = re.match("\t our (.*), std (.*), opt (.*), ari (.*), pro (.*), moz (.*), pjg (.*)", l)
		
		baseline = int(m.group(2))
		our.append(get_ratio(int(m.group(1)), baseline))
		#std.append(get_ratio(int(m.group(1)), baseline))
		opt.append(get_ratio(int(m.group(3)), baseline))
		ari.append(get_ratio(int(m.group(4)), baseline))
		pro.append(get_ratio(int(m.group(5)), baseline))
		#moz.append(get_ratio(int(m.group(6)), baseline))
		moz.append(get_ratio(int(m.group(6)), baseline))
		pjg.append(get_ratio(int(m.group(7)), baseline))
		now_f += 1
		break

print our
print opt
print ari
print pro
print moz
fig = plt.figure()
grid()
ax = fig.add_subplot(111)    # The big subplot

fig = plt.figure()
grid()
ax = fig.add_subplot(111)    # The big subplot
#ax.plot(our, "-o")
ax.plot(our, "-x", ms=15)
ax.plot(opt, "-o", ms=15)
ax.plot(ari, "-d", ms=15)
ax.plot(pro, "-s", ms=15)
ax.plot(moz, "-p", ms=15)
ax.plot(pjg, "-^", ms=15)
ax.set_ylim([0, 35])
ax.set_xlim([-0.5, 8.5])
ax.legend(["NAME", "OPT", "ARI", "PRO", "MOZ", "PJG"], fontsize=22, numpoints=1, ncol=3)
ax.set_xlabel("Quality Parameter", fontsize=24)
ax.set_ylabel("Compression (100%)", fontsize=24)
plt.tick_params(axis='both', which='major', labelsize=22)
plt.tick_params(axis='both', which='minor', labelsize=22)
plt.xticks(range(len(folders)), folders)
#plt.tick_params(axis='both', which='major', labelsize=30)
#plt.tick_params(axis='both', which='minor', labelsize=30)
plt.tight_layout()
#fig.savefig("filesize.eps", bbox_inches='tight')
fig.savefig("tecnick_quality.png", bbox_inches='tight')
fig.savefig("tecnick_quality.eps", bbox_inches='tight')

f_out = open("f_10_a.csv", "w")
i = 0
for x in folders:
	f_out.write(x+",")
	f_out.write(str(our[i])+",")
	f_out.write(str(opt[i])+",")
	f_out.write(str(ari[i])+",")
	f_out.write(str(pro[i])+",")
	f_out.write(str(moz[i])+",")
	f_out.write(str(pjg[i])+",")
	f_out.write("\n")
	i+=1
f_out.close()