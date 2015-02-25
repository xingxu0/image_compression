import os, commands, re, sys

folders = ['100', '200', '300', '400', '600', '800', '1000', '1200']
folders = ['600','1200']

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
	for i in range(1, 101):#101):
		#if i == 1 or i == 20:
		#	continue
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -encode tbl_" + f + "_23dc" + " images/" + f + "_Q75/" + str(i) + ".jpg temp_our.jpg")
		print c
		m = re.match("Total saving: (.*) bits\nOriginal filesize: (.*), encoded filesize: (.*), saving: (.*)\nTotal time elapsed : (.*) us", c[1])
		our_encoding_time += int(m.group(5))

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -decode tbl_" + f + "_23dc" + " temp_our.jpg " + str(i) + "temp.jpg")
		print c
		m = re.match("Total time elapsed : (.*) us", c[1])
		our_decoding_time += int(m.group(1))

		# sample output: Total saving: 134751 bits\nOriginal filesize: 106207, encoded filesize: 89350, saving: 0.158718\nTotal time elapsed : 65678 us'
		#m = re.match("Total saving: (.*) bits\nOriginal filesize: (.*), encoded filesize: (.*), saving: (.*)\nTotal time elapsed : (.*) us", c[1])
		#continue
		#c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -decode tbl_" + "600" + "_all_default" + " temp.jpg " + str(i) + "_out.jpg")
		#c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -decode ../image_compression_github/image_compression/tbl_" + f + "_q75" + " temp.jpg " + str(i) + "_out.jpg")
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -arithmetic images/" + f + "_Q75/" + str(i) + ".jpg temp_ari.jpg")
		m = re.match("Total time elapsed : (.*) us", c[1])
		ari_encoding_time += int(m.group(1))

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran temp_ari.jpg temp.jpg")
		m = re.match("Total time elapsed : (.*) us", c[1])
		ari_decoding_time += int(m.group(1))

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -optimize images/" + f + "_Q75/" + str(i) + ".jpg temp_opt.jpg")
		m = re.match("Total time elapsed : (.*) us", c[1])
		opt_encoding_time += int(m.group(1))

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran temp_opt.jpg temp.jpg")
		m = re.match("Total time elapsed : (.*) us", c[1])
		opt_decoding_time += int(m.group(1))


		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -progressive images/" + f + "_Q75/" + str(i) + ".jpg temp_ari.jpg")
		m = re.match("Total time elapsed : (.*) us", c[1])
		pro_encoding_time += int(m.group(1))

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran temp_ari.jpg temp.jpg")
		m = re.match("Total time elapsed : (.*) us", c[1])
		pro_decoding_time += int(m.group(1))

		c = commands.getstatusoutput("time -p /opt/mozjpeg/bin/jpegtran images/" + f + "_Q75/" + str(i) + ".jpg > temp_moz.jpg")
		print c
		m = re.match("real (.*)\nuser (.*)", c[1])
		moz_encoding_time += int(float(m.group(1))*1000000)

		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran temp_moz.jpg temp.jpg")
		m = re.match("Total time elapsed : (.*) us", c[1])
		moz_decoding_time += int(m.group(1))


	print f
	print "Our:"
	print "total encoding time:", our_encoding_time, "ms (", our_encoding_time/100000.0, "ms per image)"
	print "total decoding time:", our_decoding_time, "ms (", our_decoding_time/100000.0, "ms per image)"

	print "Opt:"
	print "total encoding time:", opt_encoding_time, "ms (", opt_encoding_time/100000.0, "ms per image)"
	print "total decoding time:", opt_decoding_time, "ms (", opt_decoding_time/100000.0, "ms per image)"

	print "Ari:"
	print "total encoding time:", ari_encoding_time, "ms (", ari_encoding_time/100000.0, "ms per image)"
	print "total decoding time:", ari_decoding_time, "ms (", ari_decoding_time/100000.0, "ms per image)"

	print "Pro:"
	print "total encoding time:", pro_encoding_time, "ms (", pro_encoding_time/100000.0, "ms per image)"
	print "total decoding time:", pro_decoding_time, "ms (", pro_decoding_time/100000.0, "ms per image)"

	print "Moz:"
	print "total encoding time:", moz_encoding_time, "ms (", moz_encoding_time/100000.0, "ms per image)"
	print "total decoding time:", moz_decoding_time, "ms (", moz_decoding_time/100000.0, "ms per image)"

	print "\n"
