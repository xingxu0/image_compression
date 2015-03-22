import glob, os, sys, re, math, operator
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from pylab import *

def get_ratio(a, b):
	return (b-a)*1.0/b*100

folders = ['30','40','50','60','70','80','90']
folders = ['50','55','60','65','70','75','80','90','95']

our = {}
std = {}
opt = {}
ari = {}
pro = {}
moz = {}

ls = open("mit5k_100.csv").readlines()
for l in ls:
	if l.find(",,,,,,,") != -1:
		res = l[:l.find(",,,,,,,")]
		our[res] = {}
		std[res] = {}
		opt[res] = {}
		ari[res] = {}
		pro[res] = {}
		moz[res] = {}
		

i = 0
print len(ls)
while i < len(ls):
	l = ls[i]
	print l
	if l.find(",,,,,,,") != -1:
		c_res = l[:l.find(",,,,,,,")]
	else:
		n = l.split(",")
		# aspect ratio 4:3,50,776636,925187,872875,806557,888755,862437
		baseline = int(n[3])
		q = n[1]
		print q
		our[c_res][q] = get_ratio(int(n[2]), baseline)
		opt[c_res][q] = get_ratio(int(n[4]), baseline)
		ari[c_res][q] = get_ratio(int(n[5]), baseline)
		pro[c_res][q] = get_ratio(int(n[6]), baseline)
		moz[c_res][q] = get_ratio(int(n[7]), baseline)
	i += 1

print our
print opt
print ari
print pro
print moz
ress = ['320x240', '800x600', '1152x864', '1400x1050', '1600x1200', '2048x1536']
qs = ['50','55','60','65','70','75','80','90','95']

t_ress = []
for x in ress:
	t_ress.append(x[:x.find("x")])

# fix q
for q in qs:
	our_ = []
	opt_ = []
	ari_ = []
	pro_ = []
	moz_ = []
	for r in ress:
		our_.append(our[r][q])
		opt_.append(opt[r][q])
		ari_.append(ari[r][q])
		pro_.append(pro[r][q])
		moz_.append(moz[r][q])
	fig = plt.figure()
	grid()
	ax = fig.add_subplot(111)    # The big subplot
	ax.plot(our_, "-x", ms=15)
	ax.plot(opt_, "-o", ms=15)
	ax.plot(ari_, "-d", ms=15)
	ax.plot(pro_, "-s", ms=15)
	ax.plot(moz_, "-p", ms=15)
	ax.set_ylim([0, 25])
	#ax.set_xlim([-0.5, 6.5])
	ax.set_xlim([-0.5, 5.5])
	ax.legend(["NAME", "OPT", "ARI", "PRO", "MOZ"], fontsize=22, numpoints=1, ncol=3)
	ax.set_xlabel("Resolution (X by 0.75X)", fontsize=24)
	ax.set_ylabel("Compression (100%)", fontsize=24)
	plt.tick_params(axis='both', which='major', labelsize=22)
	plt.tick_params(axis='both', which='minor', labelsize=22)
	plt.xticks(range(len(ress)), t_ress)#, rotation='30')
	#plt.tick_params(axis='both', which='major', labelsize=30)
	#plt.tick_params(axis='both', which='minor', labelsize=30)
	plt.tight_layout()
	#fig.savefig("filesize.eps", bbox_inches='tight')
	fig.savefig("fivek_quality_%s.png"%(q), bbox_inches='tight')
	fig.savefig("fivek_quality_%s.eps"%(q), bbox_inches='tight')
	#fig.savefig("fivek_quality.eps", bbox_inches='tight')

# fix q
for r in ress:
	our_ = []
	opt_ = []
	ari_ = []
	pro_ = []
	moz_ = []
	for q in qs:
		our_.append(our[r][q])
		opt_.append(opt[r][q])
		ari_.append(ari[r][q])
		pro_.append(pro[r][q])
		moz_.append(moz[r][q])
	fig = plt.figure()
	grid()
	ax = fig.add_subplot(111)    # The big subplot
	ax.plot(our_, "-x", ms=15)
	ax.plot(opt_, "-o", ms=15)
	ax.plot(ari_, "-d", ms=15)
	ax.plot(pro_, "-s", ms=15)
	ax.plot(moz_, "-p", ms=15)
	ax.set_ylim([0, 30])
	#ax.set_xlim([-0.5, 6.5])
	ax.legend(["NAME", "OPT", "ARI", "PRO", "MOZ"], fontsize=22, numpoints=1, ncol=3)
	ax.set_xlabel("Quality", fontsize=24)
	ax.set_ylabel("Compression (100%)", fontsize=24)
	plt.tick_params(axis='both', which='major', labelsize=22)
	plt.tick_params(axis='both', which='minor', labelsize=22)
	plt.xticks(range(len(qs)), qs, rotation='30')
	#plt.tick_params(axis='both', which='major', labelsize=30)
	#plt.tick_params(axis='both', which='minor', labelsize=30)
	plt.tight_layout()
	#fig.savefig("filesize.eps", bbox_inches='tight')
	fig.savefig("fivek_filesize_%s.png"%(r), bbox_inches='tight')
	#fig.savefig("fivek_quality.eps", bbox_inches='tight')




exit()

fig = plt.figure()
grid()
ax = fig.add_subplot(111)    # The big subplot
#ax.plot(our, "-o")
ax.plot(our, "-x", ms=15)
ax.plot(opt, "-o", ms=15)
ax.plot(ari, "-d", ms=15)
ax.plot(pro, "-s", ms=15)
ax.plot(moz, "-p", ms=15)
ax.set_ylim([0, 25])
ax.set_xlim([-0.5, 6.5])
ax.legend(["NAME", "OPT", "ARI", "PRO", "MOZ"], fontsize=22, numpoints=1, ncol=3)
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