import glob, os, sys, re, math, operator
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from pylab import *

ls = open("cdf.out").readlines()
d = []
for l in ls:
	d.append(100*float(l[l.find(":")+1:]))
print d

s = min(d)
e = max(d)
print s,e

x = []
y = []
i = 0
while i<e+0.1:
	x.append(i)
	y.append(0)
	i += 0.05

for i in range(len(x)):
	if i == 0:
		continue
	y[i]=y[i-1]
	for dd in d:
		if dd>x[i-1] and dd<=x[i]:
			y[i] += 1

ss = len(d)
print ss
for i in range(len(y)):
	y[i]*=1.0/ss

fig = plt.figure()
ax = fig.add_subplot(111)    # The big subplot
#ax.set_xscale('log')
ax.plot(x,y,'b')
#ec = ['b','g','r','c','m','y']
#hatch=["/","-", "+","x","O","//"]
grid()
ax.set_ylim([-0.05, 1.05])
ax.set_xlim([0, 100])
ax.set_xlabel("Compression (100%)", fontsize=24)
ax.set_ylabel("CDF", fontsize=24)
plt.tick_params(axis='both', which='major', labelsize=22)
plt.tick_params(axis='both', which='minor', labelsize=22)
#plt.xticks(range(len(folders)), folders)#, rotation='vertical')
#plt.tick_params(axis='both', which='major', labelsize=30)
#plt.tick_params(axis='both', which='minor', labelsize=30)
a = axes([.4, .25, .5, .5])
plot([0, 1000], [0, 1000], '-.k')
a.plot(x,y,'r')
title('[10, 25] Zoom In', fontsize=20)
setp(a, xlim=(10,25), ylim=(-0.01, 1.05))
#setp(a, xticks=[499.5, 500.0, 500.5], yticks=[0, 250, 500])
tick_params(axis='both', which='major', labelsize=20)
tick_params(axis='both', which='minor', labelsize=20)

grid()
plt.tight_layout()
#fig.savefig("filesize.eps", bbox_inches='tight')
fig.savefig("facebook_cdf.png", bbox_inches='tight')
fig.savefig("facebook_cdf.eps", bbox_inches='tight')