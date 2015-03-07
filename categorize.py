import os, sys, glob, commands

folder = sys.argv[1]
fs = glob.glob("%s/*.jpg"%(folder)) + glob.glob("%s/*.jpeg"%(folder))

q_bucket = range(0, 100, 10)
f_bucket = {}

for q in q_bucket:
	commands.getstatusoutput("mkdir q_%s"%(q))
	f_bucket[q] = 0

for f in fs:
	c = commands.getstatusoutput("identify -verbose %s | grep Quality"%(f))
	if c[1].find("Quality:") == -1:
		continue
	q = int(c[1][c[1].find("Quality:") + 8:])
	q_ = q / 10 * 10
	commands.getstatusoutput("cp %s q_%s/"%(f, q_))
	f_bucket[q_] += 1

print f_bucket