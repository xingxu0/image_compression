import os, commands, re, sys

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
for f in folders:
	total_optimized_size = 0
	total_encoded_size = 0
	total_encoding_time = 0
	total_decoding_time = 0
	for i in range(1, 101):#101):
		#if i == 1 or i == 20:
		#	continue
		print i
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -encode ../image_compression_github/image_compression/tbl_" + "600" + "_all_default" + " images/" + f + "_Q75/" + str(i) + ".jpg temp.jpg")
		#c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -encode ../image_compression_github/image_compression/tbl_" + f + "_q75" + " images/" + "1200" + "_Q75/" + str(i) + ".jpg temp.jpg")

		print c
		# sample output: Total saving: 134751 bits\nOriginal filesize: 106207, encoded filesize: 89350, saving: 0.158718\nTotal time elapsed : 65678 us'
		m = re.match("Total saving: (.*) bits\nOriginal filesize: (.*), encoded filesize: (.*), saving: (.*)\nTotal time elapsed : (.*) us", c[1])
		saving_bits = int(m.group(1))
		jpg_opt_size = int(m.group(2))
		out_size = int(m.group(3))
		saving_percent = float(m.group(4))
		encoding_time = int(m.group(5))
		total_optimized_size += jpg_opt_size
		total_encoded_size += out_size
		total_encoding_time += encoding_time
		c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -decode ../image_compression_github/image_compression/tbl_" + "600" + "_all_default" + " temp.jpg " + str(i) + "_out.jpg")
		#c = commands.getstatusoutput("/opt/libjpeg-turbo/bin/jpegtran -decode ../image_compression_github/image_compression/tbl_" + f + "_q75" + " temp.jpg " + str(i) + "_out.jpg")

		print c
		# sample output: Total time elapsed : 46321 us
		m = re.match("Total time elapsed : (.*) us", c[1])
		decoding_time = int(m.group(1))
		total_decoding_time += decoding_time
	if first_seen == False:
		base_encode = total_encoding_time/100000.0
		base_decode = total_decoding_time/100000.0
		base_x = int(f)
		first_seen = True
	x.append(int(f)*int(f))
	y_encoding.append(base_encode*(int(f)/base_x)*(int(f)/base_x))
	y_decoding.append(base_decode*(int(f)/base_x)*(int(f)/base_x))
	encoding.append(total_encoding_time/100000.0)
	decoding.append(total_decoding_time/100000.0)
	gain_ratio.append((total_optimized_size-total_encoded_size)*1.0/total_optimized_size)
	print ""
	print f
	print "total opt size:", total_optimized_size, "total encoded size:", total_encoded_size, "(", (total_optimized_size-total_encoded_size)*1.0/total_optimized_size, " saving)"
	print "total encoding time:", total_encoding_time, "ms (", total_encoding_time/100000.0, "ms per image)"
	print "total decoding time:", total_decoding_time, "ms (", total_decoding_time/100000.0, "ms per image)"
