import os, commands, re, sys

folders = ['200', '300', '400', '600', '800', '1000', '1200']
encoding = []
decoding = []
encoding_lossy = []
decoding_lossy = []

for f in folders:
	total_encoding_time = 0
	total_decoding_time = 0
	total_encoding_time_lossy = 0
	total_decoding_time_lossy = 0
	for i in range(1, 101):#101):
		print i
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -encode fb_number_exp/1200_fb_test/table images/generate_" + f + "_75/" + str(i) + ".jpg temp33.jpg")
		print c
		m = re.match("Total saving: (.*) bits\nOriginal filesize: (.*), encoded filesize: (.*), saving: (.*)\nTotal time elapsed : (.*) us", c[1])
		encoding_time = int(m.group(5))
		total_encoding_time += encoding_time
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -decode fb_number_exp/1200_fb_test/table  temp33.jpg " + str(i) + "temp33_out.jpg")
		print c
		m = re.match("Total time elapsed : (.*) us", c[1])
		decoding_time = int(m.group(1))
		total_decoding_time += decoding_time

		c = commands.getstatusoutput("/opt/libjpeg-turbo-lossy/bin/jpegtran -encode fb_number_exp/1200_fb_test/table 2.0 0.4 images/generate_" + f + "_75/" + str(i) + ".jpg temp33.jpg")
		print c
		m = re.match("Total saving: (.*) bits\nOriginal filesize: (.*), encoded filesize: (.*), saving: (.*)\nTotal time elapsed : (.*) us", c[1])
		encoding_time = int(m.group(5))
		total_encoding_time_lossy += encoding_time
		c = commands.getstatusoutput("/opt/libjpeg-turbo-lossy/bin/jpegtran -decode fb_number_exp/1200_fb_test/table  temp33.jpg " + str(i) + "temp33_out.jpg")
		print c
		m = re.match("Total time elapsed : (.*) us", c[1])
		decoding_time = int(m.group(1))
		total_decoding_time_lossy += decoding_time

	encoding.append(total_encoding_time/100000.0)
	decoding.append(total_decoding_time/100000.0)
	encoding_lossy.append(total_encoding_time_lossy/100000.0)
	decoding_lossy.append(total_decoding_time_lossy/100000.0)

	print ""
	print f
	print "total encoding time:", total_encoding_time, "ms (", total_encoding_time/100000.0, "ms per image)"
	print "total decoding time:", total_decoding_time, "ms (", total_decoding_time/100000.0, "ms per image)"
	print ""
	print "total encoding time lossy:", total_encoding_time_lossy, "ms (", total_encoding_time_lossy/100000.0, "ms per image)"
	print "total decoding time lossy:", total_decoding_time_lossy, "ms (", total_decoding_time_lossy/100000.0, "ms per image)"

