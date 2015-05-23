# this file is to plot PSNR / rate curve for different quality factor, and by zero-off of using different threshold
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, sys, glob, commands
import matplotlib.gridspec as gridspec
from pylab import *

reso = "1200"

qs=[100,95]
x={}
y={}
x[100]=[150.72356 , 155.84239 , 160.73232 , 167.67344 , 175.40073 , 182.74827 , 189.96761 , 202.08919 , 212.50768 , 227.18504 , 244.10105 , 260.02672 , 282.2735 , 310.51632 , 349.72822 , 400.35632 , 486.71131 , 626.47872 ,]
y[100]=[34.415003 , 34.557692 , 34.73568 , 34.915518 , 35.1311 , 35.311593 , 35.505787 , 35.793013 , 36.002101 , 36.312095 , 36.621887 , 36.976169 , 37.371131 , 37.837467 , 38.42063 , 39.100298 , 39.988514 , 41.232558 ,]

x[95]=[189.1219 , 192.8946 , 200.05718 , 207.10713 , 211.89942 , 221.90492 , 232.55868 , 237.99489 , 247.77801 , 253.15897 , 259.28034 , 269.19036 , 275.48855 , 290.94222 , 308.47708 , 356.85157 , 388.97347 , 402.08797 , 428.70957 , 457.15632 , 486.71131 ,]
y[95]=[35.220247 , 35.327668 , 35.450415 , 35.517682 , 35.576288 , 35.669365 , 35.806899 , 35.982857 , 36.167549 , 36.338619 , 36.535611 , 36.688111 , 36.807387 , 36.887576 , 36.86193 , 36.656121 , 36.796674 , 37.313729 , 37.982536 , 38.678066 , 39.988514 ,]

#from 85
r1=[197.35, 200.479, 209.738,215.896,226.12, 235.19, 240.5,  248.55, 252.32, 258.69, 259.248,  259.280]
r1_=[35.26, 35.45, 35.80,35.96,      36.19,  36.34,  36.428, 36.495, 36.517, 36.535, 36.5356,  36.536]


r2=[182.41,185.82,192.18,       192.895]
r2_=[35.25, 35.29, 35.326,      35.3277]

r3 = [181.736,189.322,193.038,199.441,                  200.0572]
r3_ = [35.257,35.376, 35.417, 35.449,               35.45042]


fig = plt.figure()
ax = fig.add_subplot(111)
leg = []
for t in qs:
	#ax.plot(x[t], y[t], '-x')
	if t != 100:
		ax.plot(x[t], y[t], ':xb', lw=1,ms=10)
		leg.append("Trans. from QP="+str(t)+" to 75")
	else:
		ax.plot(x[t], y[t], '-k', lw=1)
		leg.append("Trans. from raw")
	print "#",t
	for tt in x[t]:
		print tt,",",
	print ""
	for tt in y[t]:
		print tt,",",
	print ""
leg.append("L-ROMP from QP=77 to 75")
ax.plot(r3, r3_, '-r+', lw=1, ms=10)
#ax.plot(r2, r2_, '-bx', lw=1, ms=10)
ax.set_xlabel("Filesize (KB)", fontsize=24)
ax.grid()
ax.set_ylabel("PSNR (dB)", fontsize=24)
#ax.legend(leg, 4)
ax.legend(leg, 2, fontsize=18, numpoints=1, ncol=1)

#ax2.legend(leg, 4)
tight_layout()
plt.tick_params(axis='both', which='major', labelsize=22)
plt.tick_params(axis='both', which='minor', labelsize=22)
savefig("Q_psnr_transcoding_new_95_2_%s.png"%(reso))
