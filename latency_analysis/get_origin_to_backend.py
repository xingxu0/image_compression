import os, pickle

OB_x = [1,3,5,7,10,30,50,70,100,300,500,700,1000,3000,5000,7000,10000]
OB_y = [0.0198586,0.137056,0.14988,0.16166,0.215622,0.875385,0.949121,0.969343,0.980389,0.991751,0.99376,0.994784,0.995669,0.998924,0.999957,0.999999,1] 

x = []
y = []

p = OB_y[0]
last_x = 0
for i in range(len(OB_x)):
	if i==0:
		p = OB_y[0]
	else:
		p = OB_y[i] - OB_y[i-1]
	N = OB_x[i] - last_x
	p /= N
	for j in range(last_x + 1, OB_x[i] + 1):
		x.append(j)
		y.append(p)
	last_x = OB_x[i]

print x

with open("origin_to_backend" + ".obj_pdf", 'wb') as f_out:
	pickle.dump((x,y), f_out)

p = 0.0
for i in range(0,10000):
	p += y[i]
print "p", p
