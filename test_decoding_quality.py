import os, commands, re, sys
import numpy as np

folders = ['100', '200', '300', '400', '600', '800', '1000', '1200']
folders = ['1200']
folders = ['50','55','60','65','70','75','80','85','90','95']

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
for f in folders:
	t_size = 0
	our_encoding_time = 0
	ari_encoding_time = 0
	pro_encoding_time = 0
	our_decoding_time = 0
	ari_decoding_time = 0
	pro_decoding_time = 0
	moz_encoding_time = 0
	moz_decoding_time = 0
	opt_encoding_time = 0
	opt_decoding_time = 0
	pjg_encoding_time = 0
	pjg_decoding_time = 0
	our_e = []
	our_d = []
	ari_e = []
	ari_d = []
	pro_e = []
	pro_d = []
	moz_e = []
	moz_d = []
	opt_e = []
	opt_d = []
	pjg_e = []
	pjg_d = []
	rsz_time = 0
	rsz_e = []
	for i in range(1, 101):
		#if i == 1 or i == 20:
		#	continue
		t_size += os.path.getsize("images/generate_1200x1200_"+ f +"/" + str(i) + ".jpg")
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -encode tbl_1200_23dc" + " images/generate_1200x1200_"+ f +"/" + str(i) + ".jpg temp_our.jpg")
		# sample output: Total saving: 134751 bits\nOriginal filesize: 106207, encoded filesize: 89350, saving: 0.158718\nTotal time elapsed : 65678 us'
		m = re.match("Total saving: (.*) bits\nOriginal filesize: (.*), encoded filesize: (.*), saving: (.*)\nTotal time elapsed : (.*) us", c[1])
		our_encoding_time += int(m.group(5))
		our_e.append(int(m.group(5)))

		#continue
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -decode tbl_1200_23dc  temp_our.jpg " + str(i)+"temp.jpg")
		m = re.match("Total time elapsed : (.*) us", c[1])
		our_decoding_time += int(m.group(1))
		our_d.append(int(m.group(1)))

		
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -arithmetic images/generate_1200x1200_" + f + "/" + str(i) + ".jpg temp_ari.jpg")
		m = re.match("Total time elapsed : (.*) us", c[1])
		ari_encoding_time += int(m.group(1))
		ari_e.append(int(m.group(1)))

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran temp_ari.jpg temp.jpg")
		m = re.match("Total time elapsed : (.*) us", c[1])
		ari_decoding_time += int(m.group(1))
		ari_d.append(int(m.group(1)))

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -optimize images/generate_1200x1200_" + f + "/" + str(i) + ".jpg temp_opt.jpg")
		m = re.match("Total time elapsed : (.*) us", c[1])
		opt_encoding_time += int(m.group(1))
		opt_e.append(int(m.group(1)))

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran temp_opt.jpg temp.jpg")
		m = re.match("Total time elapsed : (.*) us", c[1])
		opt_decoding_time += int(m.group(1))
		opt_d.append(int(m.group(1)))

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -progressive images/generate_1200x1200_" + f + "/" + str(i) + ".jpg temp_ari.jpg")
		m = re.match("Total time elapsed : (.*) us", c[1])
		pro_encoding_time += int(m.group(1))
		pro_e.append(int(m.group(1)))

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran temp_ari.jpg temp.jpg")
		m = re.match("Total time elapsed : (.*) us", c[1])
		pro_decoding_time += int(m.group(1))
		pro_d.append(int(m.group(1)))

		c = commands.getstatusoutput("time -p /opt/mozjpeg/bin/jpegtran images/generate_1200x1200_" + f + "/" + str(i) + ".jpg > temp_moz.jpg")
		#print c
		m = re.match("real (.*)\nuser (.*)", c[1])
		moz_encoding_time += int(float(m.group(1))*1000000)
		moz_e.append(int(float(m.group(1))*1000000))

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran temp_moz.jpg temp.jpg")
		m = re.match("Total time elapsed : (.*) us", c[1])
		moz_decoding_time += int(m.group(1))
		moz_d.append(int(m.group(1)))

		c = commands.getstatusoutput("time -p ./packJPG images/generate_1200x1200_" +f + "/" + str(i)+ ".jpg &>temppp")
		m = re.match("(.*)real (.*)\nuser (.*)", c[1], re.DOTALL)
		#print m.group(2)
		pjg_encoding_time += int(float(m.group(2))*1000000)
		pjg_e.append(int(float(m.group(2))*1000000))

		c = commands.getstatusoutput("time -p ./packJPG images/generate_1200x1200_" +f + "/" + str(i)+ ".pjg &>temppp")
		m = re.match("(.*)real (.*)\nuser (.*)", c[1], re.DOTALL)
		#print m.group(2)
		pjg_decoding_time += int(float(m.group(2))*1000000)
		pjg_d.append(int(float(m.group(2))*1000000))
		commands.getstatusoutput("rm images/generate_1200x1200_" + f + "/*.pjg")

		c = commands.getstatusoutput("time -p convert -limit thread 1 -resize %dx%d images/generate_1200x1200_"%(int(1200)/2,int(1200)/2) +f + "/" + str(i)+ ".jpg tempp.jpg")
		m = re.match("(.*)real (.*)\nuser (.*)", c[1], re.DOTALL)
		#print m.group(2)
		rsz_time += int(float(m.group(2))*1000000)
		rsz_e.append(int(float(m.group(2))*1000000))

	print f, t_size
	print "Our:"
	print "total encoding time:", our_encoding_time, "ms (", our_encoding_time/100000.0, "ms per image)", np.std(our_e)/np.mean(our_e)
	print "total decoding time:", our_decoding_time, "ms (", our_decoding_time/100000.0, "ms per image)", np.std(our_d)/np.mean(our_d)

	print "Opt:"
	print "total encoding time:", opt_encoding_time, "ms (", opt_encoding_time/100000.0, "ms per image)", np.std(opt_e)/np.mean(opt_e)
	print "total decoding time:", opt_decoding_time, "ms (", opt_decoding_time/100000.0, "ms per image)", np.std(opt_d)/np.mean(opt_d)

	print "Ari:"
	print "total encoding time:", ari_encoding_time, "ms (", ari_encoding_time/100000.0, "ms per image)", np.std(ari_e)/np.mean(ari_e)
	print "total decoding time:", ari_decoding_time, "ms (", ari_decoding_time/100000.0, "ms per image)", np.std(ari_d)/np.mean(ari_d)

	print "Pro:"
	print "total encoding time:", pro_encoding_time, "ms (", pro_encoding_time/100000.0, "ms per image)", np.std(opt_e)/np.mean(opt_e)
	print "total decoding time:", pro_decoding_time, "ms (", pro_decoding_time/100000.0, "ms per image)", np.std(opt_d)/np.mean(opt_d)

	print "Moz:"
	print "total encoding time:", moz_encoding_time, "ms (", moz_encoding_time/100000.0, "ms per image)", np.std(moz_e)/np.mean(moz_e)
	print "total decoding time:", moz_decoding_time, "ms (", moz_decoding_time/100000.0, "ms per image)", np.std(moz_d)/np.mean(moz_d)

	print "Pjg:"
	print "total encoding time:", pjg_encoding_time, "ms (", pjg_encoding_time/100000.0, "ms per image)", np.std(pjg_e)/np.mean(pjg_e)
	print "total decoding time:", pjg_decoding_time, "ms (", pjg_decoding_time/100000.0, "ms per image)", np.std(pjg_d)/np.mean(pjg_d)

	print "Rsz:"
	print "total rsz time:", rsz_time, "ms (", rsz_time/100000.0, "ms per image)", np.std(rsz_e)/np.mean(rsz_e)

	print "\n"
