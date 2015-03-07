# export the blocks of JPEGs of [INPUT FOLDER] to [OUTPUT FOLDER]

import os, sys, glob

if len(sys.argv) != 3:
	print "usage: python export_coefs.py [INPUT FOLDER] [OUTPUT FOLDER]"
	exit()

in_folder = sys.argv[1]
out_folder = sys.argv[2]
os.system("mkdir " + out_folder)

files = glob.glob(in_folder + "/*.jpg")
for f in files:
	name = f[f.rfind("/") + 1 : ]
	print name
	cmd = "jpegtran -outputcoef " + out_folder + "/" + name + ".block " + f + " temp.out"
	os.system(cmd)

os.system("rm temp.out")
