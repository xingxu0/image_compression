import huff
import os, sys

prob = [0.5, 0.3, 0.1, 0.1]

probs = sys.argv[1]
prob = probs.split(" ")
for i in range(len(prob)):
	prob[i] = float(prob[i])

codes = huff.huffman(prob)

print codes

bits = {}
for i in range(len(prob)):
	bits[i] = len(codes[i])
print bits

