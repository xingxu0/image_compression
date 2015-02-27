import os, sys, glob

q = sys.argv[1]

f = glob.glob("./*.png")

x = 0
os.system("mkdir generate" + "_" + q)
for i in f:
	x += 1	
	cmd = "convert -quality " + q  + " "  + i + " generate_" + q + "/" + str(x) +".jpg"
	os.system(cmd)
	print cmd
