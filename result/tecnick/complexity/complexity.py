import glob, os, sys, re, math, operator
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111)
enc = [47, 23, 40, 91, 209, 168]
dec = [37, 15, 40, 26, 25, 178]
x_enc = range(len(enc))
x_dec = range(len(dec))
for x in range(len(x_enc)):
	x_enc[x] -= 0.35
for x in range(len(x_dec)):
	x_dec[x] += 0.05

ax.bar(x_enc, enc, width=0.3, edgecolor='b', color='none',hatch="/")
ax.bar(x_dec, dec, width=0.3, edgecolor='r', color='none',hatch="\\")

#ax.set_xlim([-1,45])
ax.grid()
ax.legend(['Encoding', 'Decoding'], 2, fontsize=22)
ax.set_xticks(range(len(enc)))
ax.set_xticklabels(['NAME', 'OPT', 'ARI', 'PRO', 'MOZ', 'PJG'])
ax.set_ylabel("Time (ms)", fontsize=24)
ax.tick_params(axis='both', which='major', labelsize=22)
ax.tick_params(axis='both', which='minor', labelsize=22)
plt.tight_layout()
fig.savefig("tecnick_complexity.eps", bbox_inches='tight')
fig.savefig("tecnick_complexity.png", bbox_inches='tight')