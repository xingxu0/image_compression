import os, commands, re, sys
import matplotlib.pyplot as plt
from pylab import *

folders = ['100', '200', '300', '400', '600', '800', '1000', '1200']
#folders = ['600']

x = []
y_encoding = []
y_decoding = []
encoding = []
decoding = []
gain_ratio = []

first_seen = False
base_encode = 0
base_decode = 0
base_x = 0
fig = plt.figure()
ax = fig.add_subplot(111)
co = ["r", "y", "b", "g", "k"]
ma = ["x", "o", "v", "^", "s"]
for f in folders:
	total_std_size = 0
	total_opt_size = 0
	total_our_size = 0
	total_ari_size = 0
	total_pro_size = 0
	total_moz_size = 0
	total_our_time = 0
	total_opt_time = 0
	total_ari_time = 0
	total_pro_time = 0
	total_moz_time = 0

	fig = plt.figure()
	ax = fig.add_subplot(111)
	for i in range(1, 101):
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -encode ../image_compression_github/image_compression/tbl_" + f + "_1_9_new" + " images/" + f + "_Q75/" + str(i) + ".jpg temp.jpg")
		#print c
		# sample output: Total saving: 134751 bits\nOriginal filesize: 106207, encoded filesize: 89350, saving: 0.158718\nTotal time elapsed : 65678 us'
		m = re.match("Total saving: (.*) bits\nOriginal filesize: (.*), encoded filesize: (.*), saving: (.*)\nTotal time elapsed : (.*) us", c[1])
		out_size = int(m.group(3))
		encoding_time = int(m.group(5))
		total_our_size += out_size
		total_our_time += encoding_time

		os.system("jpegtran -outputcoef t images/" + f + "_Q75/" + str(i) + ".jpg temp.jpg")
		total_std_size += os.path.getsize("temp.jpg")

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -optimize images/" + f + "_Q75/" + str(i) + ".jpg temp.jpg")
		total_opt_size += os.path.getsize("temp.jpg")
		m = re.match("Total time elapsed : (.*) us", c[1])
		total_opt_time += int(m.group(1))

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -arithmetic images/" + f + "_Q75/" + str(i) + ".jpg temp.jpg")
		total_ari_size += os.path.getsize("temp.jpg")
		m = re.match("Total time elapsed : (.*) us", c[1])
		total_ari_time += int(m.group(1))


		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -progressive images/" + f + "_Q75/" + str(i) + ".jpg temp.jpg")
		total_pro_size += os.path.getsize("temp.jpg")
		m = re.match("Total time elapsed : (.*) us", c[1])
		total_pro_time += int(m.group(1))

		c = commands.getstatusoutput("time -p /opt/mozjpeg/bin/cjpeg -notrellis -notrellis-dc images/" + f + "_Q75/" + str(i) + ".jpg > temp.jpg")
		total_moz_size += os.path.getsize("temp.jpg")
		m = re.match("real (.*)\nuser (.*)", c[1])
		total_moz_time += int(float(m.group(1))*1000000)


	x = [(total_std_size-total_our_size)*1.0/total_std_size]
	y = [total_our_time/100000.0]
	ax.scatter(y, x, c=co[0], marker=ma[0])
	print x, y

	x = [(total_std_size-total_opt_size)*1.0/total_std_size]
	y = [total_opt_time/100000.0]
	ax.scatter(y, x, c=co[1], marker=ma[1])
	print x, y

	x = [(total_std_size-total_ari_size)*1.0/total_std_size]
	y = [total_ari_time/100000.0]
	ax.scatter(y, x, c=co[2], marker=ma[2])
	print x, y

	x = [(total_std_size-total_pro_size)*1.0/total_std_size]
	y = [total_pro_time/100000.0]
	ax.scatter(y, x, c=co[3], marker=ma[3])
	print x, y

	x = [(total_std_size-total_moz_size)*1.0/total_std_size]
	y = [total_moz_time/100000.0]
	ax.scatter(y, x, c=co[4], marker=ma[4])
	print x, y

	ax.set_xlabel("Encoding Time (ms)")
	ax.set_ylim([0, 0.16])
	ax.grid()
	ax.set_ylabel("Compression Ratio (%)")
	ax.legend(['ours','opt','ari','pro','moz'], 1)
	savefig("tradeoff_%s.png"%(f))

