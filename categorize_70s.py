import os, sys, glob, commands

folder = sys.argv[1]
fs = glob.glob("%s/*.jpg"%(folder)) + glob.glob("%s/*.jpeg"%(folder))

q_bucket = range(70, 80, 1)
f_bucket = {}

for q in q_bucket:
	commands.getstatusoutput("rm q_%s -rf"%(q))
	commands.getstatusoutput("mkdir q_%s"%(q))
	f_bucket[q] = 0

p = 0
last_p = 0
for f in fs:
	p += 1
	if p*100/len(fs) > last_p:
		last_p = p*100/len(fs)
		print str(last_p)+"%"
	c = commands.getstatusoutput("identify -verbose %s | grep Quality"%(f))
	if c[1].find("Quality:") == -1:
		commands.getstatusoutput("identify -verbose %s &>> missing_pics_issue.out"%(f))
		continue
	q = int(c[1][c[1].find("Quality:") + 8:])
	if q < 70 or q > 79:
		continue
	q_ = q# / 10 * 10
	commands.getstatusoutput("cp %s q_%s/"%(f, q_))
	f_bucket[q_] += 1

for q in q_bucket:
	print "quality %d:\t%d,\t%d%%"%(q, f_bucket[q], f_bucket[q]*100/p)
