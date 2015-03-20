import glob, os, sys, re, math, operator
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from pylab import *

enc = [47, 23, 40, 91, 209, 168]
dec = [37, 15, 40.2, 26, 25, 178]
com = [15.42, 2.00, 9.7, 5.90, 6.9, 20.0]
fig = plt.figure()
grid()
ax = fig.add_subplot(111)    # The big subplot

fig = plt.figure()
grid()
ax = fig.add_subplot(111)    # The big subplot
#ax.plot(our, "-o")


ax.plot([enc[0]]+[dec[0]], [com[0]]+[com[0]], "-x", ms=15)
ax.plot([enc[1]]+[dec[1]], [com[1]]+[com[1]], "-o", ms=15)
ax.plot([enc[2]]+[dec[2]], [com[2]]+[com[2]], "-d", ms=15)
ax.plot([enc[3]]+[dec[3]], [com[3]]+[com[3]], "-s", ms=15)
ax.plot([enc[4]]+[dec[4]], [com[4]]+[com[4]], "-p", ms=15)
ax.plot([enc[5]]+[dec[5]], [com[5]]+[com[5]], "-^", ms=15)
ax.set_ylim([0, 30])
#ax.set_xlim([-0.5, 6.5])
ax.legend(["NAME", "OPT", "ARI", "PRO", "MOZ", "PJG"], fontsize=22, numpoints=1, ncol=3)
ax.set_xlabel("Complexity (ms)", fontsize=24)
ax.set_ylabel("Compression (100%)", fontsize=24)
plt.tick_params(axis='both', which='major', labelsize=22)
plt.tick_params(axis='both', which='minor', labelsize=22)
#plt.xticks(range(len(folders)), folders, rotation='30')
#plt.tick_params(axis='both', which='major', labelsize=30)
#plt.tick_params(axis='both', which='minor', labelsize=30)
plt.tight_layout()
#fig.savefig("filesize.eps", bbox_inches='tight')
fig.savefig("tecnick_tradeoff.png", bbox_inches='tight')
fig.savefig("tecnick_tradeoff.eps", bbox_inches='tight')