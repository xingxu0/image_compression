# input X1, X2
# get distribution of X1 - X2
# output as X3
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
		if i % 1000 == 0:
			print "task %d %d: "%(a,b), i, int(time.time())
		x.append(i)
		p = 0.0
		for j in range(i, int(max(x1)) + 1):
			#if j-i==-3:
			#	p+=p1[j]
			#else:
			#	continue
			if j-i in p2 and j in p1: #>=x2_l and j-i<=x2_r:
				p += p2[j-i]*p1[j]
			#if j-i in x2:
				#p += y2[x2.index(j-i)]*y1[x1.index(i)]
		y.append(p)
	return x, y

def log_result(result):
	global final_x, final_y
	final_x += result[0]
	final_y += result[1]

f1 = sys.argv[1]
f2 = sys.argv[2]
f3 = sys.argv[3]
with open(f2, 'rb') as f_in:
		x2, y2 = pickle.load(f_in)
print x2
print y2
print "abcde"

with open(f1, 'rb') as f_in:
		x1, y1 = pickle.load(f_in)
print max(x1)


final_x_, final_y_ = worker(-int(max(x2))-2,1+int(max(x1)))

#print final_x
#print final_y
#print max(final_x)

final_x = []
final_y = []
t_ = 0.0
ratio = 0.0
for i in range(len(final_x_)):
	if final_x_[i] <= 0:
		t_ += final_y_[i]
	else:
		t_ += final_y_[i]
		final_x.append(final_x_[i])
		if final_x_[i] > 1:	
			final_y.append(t_+ratio)
		else:
			final_y.append(0)
			ratio = t_/max(final_x_)
			print t_, ratio
		t_ = 0.0

print max(final_x)
p=0.0
for x in final_y:
	p += x
print "p", p

with open(f3, 'wb') as f_out:
	pickle.dump((final_x,final_y), f_out)
