import glob, sys, os

folder = sys.argv[1]

print folder

fs = glob.glob(folder + "/*.table")

for f in fs:
	if f.find("_", len(folder)) == -1:
		os.system("mv " + f + " " + folder + "/pool_" + f[len(folder)+1:] )
		print f
