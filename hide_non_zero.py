import os,sys

in_ = sys.argv[1]
os.system("/opt/libjpeg-turbo/bin/jpegtran -outputcoef temp.block %s temp.out"%(in_))
out_ = sys.argv[2]
f = open(out_, "w")
ls = open("temp.block").readlines()

last_dc = {}
for l in ls:
	x = l.split(":")
	f.write(x[0]+": ")
	comp = x[0]

	xs = x[1].split(" ")
	xs = xs[1:-1]
	tt = xs[0]
	if comp in last_dc and xs[0] == last_dc[comp]:
		xs[0] = "0"
	last_dc[comp] = tt
	for x in xs:
		if int(x) == 0:
			f.write("0 ")
		else:
			f.write("x ")
	f.write("\n")
f.close()
os.system("rm temp.block")
os.system("rm temp.out")
