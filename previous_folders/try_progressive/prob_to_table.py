import sys, huff

input_file = sys.argv[1]
output_file = sys.argv[2]

input_lines = open(input_file).readlines()
out_file = open(output_file, "w")

num = int(((input_lines[0]).split(" "))[0])
out_file.write(input_lines[0])

prob = []
for i in range(1, num + 1):
	data = input_lines[i].split(" ")
	prob.append(float(data[0]))

codes = huff.huffman(prob)

bits = {}
for i in range(len(prob)):
	bits[i] = len(codes[i])

for i in range(1, num + 1):
	out_file.write(str(bits[i - 1]))
	out_file.write(input_lines[i][input_lines[i].find(" "):])
out_file.close()

