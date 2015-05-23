import os, math

quant_table = [16,  11,  10,  16,  24,  40,  51,  61, 12,  12,  14,  19,  26,  58,  60,  55, 14,  13,  16,  24,  40,  57,  69,  56, 14,  17,  22,  29,  51,  87,  80,  62, 18,  22,  37,  56,  68, 109, 103,  77, 24,  35,  55,  64,  81, 104, 113,  92, 49,  64,  78,  87, 103, 121, 120, 101, 72,  92,  95,  98, 112, 100, 103,  99]

#quant_table = [16,11,12,14,12,10,16,14,13,14]

def get_scale(q):
	if q<50:
		return 5000/q
	else:
		return 200-q*2

def get_q(b, q):
	return int((b*get_scale(q) + 50)/100)

def get_psnr(mse):
	return 20*math.log(255/pow(mse, 0.5), 10)

start_q = 75 
for d in range(50, start_q):
	mse1 = 0.0
	mse2 = 0.0
	n = 0
	for v in range(1, 256):
		for x in quant_table:
			q1 = get_q(x, d)
			q2 = get_q(x, start_q)
			v1 = round(v*1.0 / q1)
			v2 = round(round(round(v*1.0 / q2) * q2) / q1)
			#print x, q1, q2, ":", v1, v2
			e1 = v - round(v1*q1)
			e2 = v - round(v2*q1)
			#if int(e1) != int(e2):
			#	print " ",e1, e2, v, q1, q2, "(", v, round(round(v/q2)*q2),")"
			mse1 += e1*e1
			mse2 += e2*e2
			n += 1
	mse1/=n
	mse2/=n
	print d, ":", mse1, get_psnr(mse1), mse2, get_psnr(mse2), get_psnr(mse1)-get_psnr(mse2)
