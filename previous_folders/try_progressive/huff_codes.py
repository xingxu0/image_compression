import huff
import os, sys

prob = [0.5, 0.3, 0.1, 0.1]

probs = sys.argv[1]
prob = probs.split(" ")
for i in range(len(prob)):
	prob[i] = float(prob[i])

codes = huff.huffman(prob)

bits = {}
for i in range(len(prob)):
	bits[len(codes[i])] = 0

for i in range(len(prob)):
	bits[len(codes[i])] += 1

p = 0
huffsize = {}
for i in bits:
	x = bits[i]
	while x>0:
		x -= 1
		huffsize[p] = i
		p += 1 

huffsize[p] = 0
code = 0
si = huffsize[0]
p = 0
huffcode = {}
while (p < len(prob) and huffsize[p]):
	while (huffsize[p] == si):
		huffcode[p] = code
		p += 1
		code += 1
	code *= 2
	si += 1

print huffcode
