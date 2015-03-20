import glob, os, sys, re, math, operator
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from pylab import *

def get_ratio(a, b):
	return (b-a)*1.0/b*100

folders = ['100', '200', '300', '400', '600', '800', '1000', '1200']

our = []
std = []
opt = []
ari = []
pro = []
moz = []

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
		m = re.match("\t our (.*), std (.*), opt (.*), ari (.*), pro (.*), moz (.*)", l)
		
		#our.append(get_ratio(int(m.group(1)), baseline))
		std.append(get_ratio(int(m.group(1)), int(m.group(2))))
		opt.append(get_ratio(int(m.group(1)), int(m.group(3))))
		ari.append(get_ratio(int(m.group(1)), int(m.group(4))))
		pro.append(get_ratio(int(m.group(1)), int(m.group(5))))
		#moz.append(get_ratio(int(m.group(6)), baseline))
		now_f += 1
		break

print ari
fig = plt.figure()
grid()
ax = fig.add_subplot(111)    # The big subplot
#ax.plot(our, "-o")
ax.plot(std, "-o")
ax.plot(opt, "-+")
ax.plot(ari, "-|")
ax.plot(pro, "-x")
ax.plot(moz, "-*")
ax.set_ylim([0, 25])
ax.legend(["vs. std", "vs. opt", "vs. ari", "vs. pro", "vs. moz"])
ax.set_xlabel("image size")#, fontsize=32)
ax.set_ylabel("compression ratio (100%)")#, fontsize=32)
plt.xticks(range(len(folders)), folders)
#plt.tick_params(axis='both', which='major', labelsize=30)
#plt.tick_params(axis='both', which='minor', labelsize=30)
plt.tight_layout()
#fig.savefig("filesize.eps", bbox_inches='tight')
fig.savefig("filesize.png", bbox_inches='tight')