import sys, copy, os, heapq, glob, operator, pickle, lib

def check_filesize(folder):
	actual_optimized_size = 0
	actual_baseline_size = 0
	estimated_size = 0
	os.system("exiftool -all= " + folder + "/*.jpg")
	os.system("rm " + folder + "/*.jpg_original")
	
	f_jpgs = glob.glob(folder + "/*.jpg")
		
	for f in f_jpgs:
		os.system("jpegtran -outputcoef temp_coef " + f + " " + f + ".baseline")
		f_abs = os.path.getsize(f + ".baseline")
		actual_baseline_size += f_abs

		os.system("jpegtran -optimize " + f + " " + f + ".optimized")
		f_aos = os.path.getsize(f + ".optimized")
		actual_optimized_size += f_aos
		
		f_es = 0
		for c in range(3):
			comp = str(c)
			if comp == "0":
				code = lib.get_luminance_codes()
			else:
				code = lib.get_chrominance_codes()
			block = lib.get_blocks_all_in_bits("temp_coef", comp)
			for ii in range(len(block)):
				x, dc_s_bits, dc_bits, r, coef_bits = lib.get_bits_detail(block[ii], code, comp=="0")
				f_es += x
		estimated_size += f_es
			
		
		
		os.system("rm " + f + ".optimized")
		os.system("rm " + f + ".baseline")		
	print "estimated size (B):", estimated_size/8
	print "JPEG baseline  (B):", actual_baseline_size
	print "JPEG optimized (B):", actual_optimized_size
	return estimated_size/8, actual_baseline_size, actual_optimized_size
		

if len(sys.argv) < 1:
	print "usage: python check_file_size.py [IMAGE FOLDER]"
	exit()

in_folder = sys.argv[1]

check_filesize(in_folder)
