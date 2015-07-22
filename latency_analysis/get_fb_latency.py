import matplotlib
matplotlib.use('Agg')
import os, sys, glob, commands, pickle
import matplotlib.pyplot as plt
from pylab import *
import numpy


def get_cdf_x_y(a, s):
	x = []
	y = []
	s_ = sorted(a)
	now = 0
	last_y = 0
	le = len(a)
	t = 0.0
	for t in np.arange(1, max(a)+s, s):
		x.append(t)
		t_ = 0
		while now<le and s_[now] <= t:
			t_ += 1
			now += 1
		last_y += t_
		#y.append((last_y)*1.0/le) # for cdf
		y.append((t_)*1.0/le) # for pdf
	return x, y

fname = sys.argv[1]

s = []
i = 0
for f in glob.glob("stripData26thOct/*"):
	i += 1
	print i, f
	if not os.path.isdir(f):
		continue
	if not os.path.isfile(f + "/" + fname):
		continue

	f_ = open(f + "/" + fname).readlines()
	for x in f_:
		s.append(1000.0*float(x))

x, y = get_cdf_x_y(s, 1)
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_ylabel("CDF")
ax.plot(x,y)
ax.set_xlabel("Latency (ms)")
ax.grid()
ax.set_ylim([0,1.1])
savefig(fname.split(".")[0] + ".png")
plt.close("all")

with open(fname.split(".")[0] + ".obj_pdf", 'wb') as f_out:
	pickle.dump((x,y), f_out)
