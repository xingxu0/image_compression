import glob, os, sys, re, math, operator
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from pylab import *

def get_ratio(a, b):
	return (b-a)*1.0/b*100

folders = ['Orignal', 'Large']

our = []
std = []
opt = []
ari = []
pro = []
moz = []
our_lossy = []

p = {}
for i in range(6):
	p[i] = []

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
		
		baseline = int(m.group(2))
		p[0].append(get_ratio(int(m.group(1)), baseline))
		#std.append(get_ratio(int(m.group(1)), int(m.group(2))))
		p[1].append(get_ratio(int(m.group(3)), baseline))
		p[2].append(get_ratio(int(m.group(4)), baseline))
		p[3].append(get_ratio(int(m.group(5)), baseline))
		p[4].append(get_ratio(int(m.group(6)), baseline))
		p[5].append(get_ratio(int(m.group(1)), baseline) + 14)
		now_f += 1
		break

print ari
fig = plt.figure()
ax = fig.add_subplot(111)    # The big subplot
ec = ['b','g','r','c','m','y']
hatch=["/","-", "+","x","O","//"]
grid()
for i in range(6):
	x = []
	x.append(i*1.0/10-0.29)
	x.append(1+i*1.0/10-0.29)
	ax.bar(x, p[i], width=0.08, edgecolor=ec[i], color='none',hatch=hatch[i])

ax.set_ylim([0, 40])
ax.set_xlim([-0.5, 1.5])
ax.legend(["NAME", "OPT", "ARI", "PRO", "MOZ", "LOSSY"], fontsize=22, numpoints=1, ncol=3)
ax.set_xticks([0, 1])
ax.set_xticklabels(['Original', 'Large'])
#ax.set_xlabel("", fontsize=24)
ax.set_ylabel("Compression (100%)", fontsize=24)
plt.tick_params(axis='both', which='major', labelsize=22)
plt.tick_params(axis='both', which='minor', labelsize=22)
#plt.xticks(range(len(folders)), folders)#, rotation='vertical')
#plt.tick_params(axis='both', which='major', labelsize=30)
#plt.tick_params(axis='both', which='minor', labelsize=30)
plt.tight_layout()
#fig.savefig("filesize.eps", bbox_inches='tight')
fig.savefig("facebook_filesize.png", bbox_inches='tight')
fig.savefig("facebook_filesize.eps", bbox_inches='tight')