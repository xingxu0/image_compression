import lib, sys, copy, os, heapq, glob

def transform(f):
	f_out = open("%s/%s"%(output_folder, f[f.rfind("/")+1:]), 'w')
	for c in range(3):
		comp = str(c)	
		if comp == "0":
			code = lib.get_luminance_codes()
		else:
			code = lib.get_chrominance_codes()
			
		block = lib.get_blocks_all_in_bits(f, comp)
		for ii in range(len(block)):
			x, dc_s_bits, dc_bits, r, coef_bits = lib.get_bits_detail(block[ii], code, comp=="0")
			f_out.write(comp + ": ")
			s = comp + ": "
			last_non_zero = 0
			for i in range(63, 0, -1):
				if block[ii][i] != 0:
					last_non_zero = i
					break
			
				
			for i in range(1, last_non_zero + 1):
				f_out.write(str(block[ii][i]) + " ")
				s += str(block[ii][i]) + " "
			f_out.write("-2 %s\n"%(str(r)))
			s += "-2 %s\n"%(str(r))
			#print block[ii], "-->", s
	f_out.close()
		
input_folder = sys.argv[1]
output_folder = sys.argv[2]
os.system("mkdir %s"%(output_folder))

files = glob.glob(input_folder + "/*.block")
for f in files:
	transform(f)
