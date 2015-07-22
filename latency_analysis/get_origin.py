# get distribution of X1 - X2
import os, pickle, time
from multiprocessing import Process, Queue

def worker(a,b,q):
	with open("origin_to_backend.obj_pdf", 'rb') as f_in:
		x2, y2 = pickle.load(f_in)

	with open("fb_notcached.obj_pdf", 'rb') as f_in:
		x1, y1 = pickle.load(f_in)
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
			print "task %d %d: "%(a,b), "[%d]"%i, int(time.time())
		x.append(i)
		p = 0.0
		for j in range(i, int(max(x1)) + 1):
			if j-i >=x2_l and j-i<=x2_r:
				p += p2[j-i]*p1[i]
				#p += y2[x2.index(j-i)]*y1[x1.index(i)]
		y.append(p)
	q.put((x, y))
	print "[done]",a,b

final_x = []
final_y = []

with open("origin_to_backend.obj_pdf", 'rb') as f_in:
	xx2, yy2 = pickle.load(f_in)

with open("fb_notcached.obj_pdf", 'rb') as f_in:
	xx1, yy1 = pickle.load(f_in)

m = int(max(max(xx1), max(xx2)))+1
print m, int(time.time())

l = [1, m/6, 2*m/6, 3*m/6,4*m/6,5*m/6, m]


t_l = []
q = Queue()
for x in range(1, 7):
	t = Process(target=worker, args= (l[x-1], l[x]-1, q))
	t.start()
	t_l.append(t)

f_x = {}
f_y = {}
for t in t_l:
	t.join()
	(x,y) = q.get()
	i = l.index(x[0])
	f_x[i] = x
	f_y[i] = y
for i in range(len(f_x)):
	final_x +=f_x[i]
	final_y +=f_y[i]

print final_x
print final_y

with open("fb_origin.obj_pdf", 'wb') as f_out:
	pickle.dump((final_x,final_y), f_out)


