# get distribution of X1 - X2
import os, pickle, time, sys
from multiprocessing.pool import ThreadPool

def worker(a,b):
	global x1, x2, y1, y2
	x = []
	y = []
	print "start task:",a,b
	#for i in range(a, b+1):
#		x.append(i)
#		y.append(i+0.1)
#	return x,y

	x2_l = min(x2)
	x2_r = max(x2)
	p1 = {}
	p2 = {}
	for i in range(len(x1)):
		p1[x1[i]] = y1[i]
	for i in range(len(x2)):
		p2[x2[i]] = y2[i]


	for i in range(a, b + 1):
		#print i
		if i % 100 == 0:
			print "task %d %d: "%(a,b), i, int(time.time())
		x.append(i)
		p = 0.0
		for j in range(i, int(max(x1)) + 1):
			if j-i==-3:
				p+=p1[j]
			else:
				continue
			if j-i >=x2_l and j-i<=x2_r:
				p += p2[j-i]*p1[j]
			#if j-i in x2:
				#p += y2[x2.index(j-i)]*y1[x1.index(i)]
		y.append(p)
	return x, y

def log_result(result):
	global final_x, final_y
	final_x += result[0]
	final_y += result[1]

with open("origin_to_backend.obj_pdf", 'rb') as f_in:
		x2, y2 = pickle.load(f_in)

with open("fb_notcached.obj_pdf", 'rb') as f_in:
		x1, y1 = pickle.load(f_in)


final_x, final_y = worker(1,1+int(max(max(x1), max(x2))))

print final_x
print final_y

with open("fb_origin2.obj_pdf", 'wb') as f_out:
	pickle.dump((final_x,final_y), f_out)
