import os, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pylab import *
import numpy as np
import matplotlib.gridspec as gridspec



quant_table = [16,  11,  10,  16,  24,  40,  51,  61, 12,  12,  14,  19,  26,  58,  60,  55, 14,  13,  16,  24,  40,  57,  69,  56, 14,  17,  22,  29,  51,  87,  80,  62, 18,  22,  37,  56,  68, 109, 103,  77, 24,  35,  55,  64,  81, 104, 113,  92, 49,  64,  78,  87, 103, 121, 120, 101, 72,  92,  95,  98, 112, 100, 103,  99]

#quant_table = [16,11,12,14,12,10,16,14,13,14]

#quant_table = [16]

def get_scale(q):
	if q<50:
		return 5000/q
	else:
		return 200-q*2

def get_q(b, q):
	return int((b*get_scale(q) + 50)/100)

def get_psnr(mse):
	return 20*math.log(255/pow(mse, 0.5), 10)

def get_q1(v, q):
	return round(v*1.0 / q)*q

def get_q2(v, q2, q1):
	return round((round(v*1.0 / q2) * q2) / q1)*q1

x = []
y = []
y_q1 = []
y_q2 = []
y_q3 = []
e1 = []
e1_ = 0.0
e2_ = 0.0
e3_ = 0.0
e2 = []
e3 = []
qq1 = int(sys.argv[2])
qq2 = int(sys.argv[1])
q1 = get_q(quant_table[0], qq1)
q2 = get_q(quant_table[0], qq2)
r = q1*q2*3
r = 30
for v in np.arange(0, r+0.01, 0.01):
	#for v in np.arange(0, r+1, 1):
	x.append(v)
	y.append(v)
	y_q1.append(get_q1(v, q1))
	y_q2.append(get_q2(v, q2, q1)+0.1)
	y_q3.append(get_q1(v,q2))
	e1_ += pow(v-get_q1(v,q1), 2)
	e2_ += pow(v-get_q2(v,q2,q1), 2)
	e3_ += pow(v-get_q1(v,q2), 2)
	e1.append(e1_)
	e2.append(e2_+0.1)
	e3.append(e3_)

fig = plt.figure()
gs = gridspec.GridSpec(2,1,height_ratios=[7,2])
ax = plt.subplot(gs[0])
ax.plot(x, y, "--k")
ax.plot(x,y_q3)
ax.plot(x,y_q1)
ax.plot(x,y_q2)
ax.legend(["raw", "QP %d (q=%d)"%(qq2,q2),  "QP %d (q=%d)"%(qq1,q1), "QP %d->%d"%(qq2,qq1)], 2)

ax2 = plt.subplot(gs[1], sharex=ax)
ax2.plot(x, e3)
ax2.plot(x, e1)
ax2.plot(x, e2)
ax2.set_xlabel("Coefficient")
ax2.set_ylabel("Squared Error")
ax.set_ylabel("Compressed Coefficient")
tight_layout()
savefig("quant_error_plot_%d_%d_1.png"%(qq1, qq2))





