# make symbol table
# python make_table.py file_1,file_2,file_3 -portion 100 // do 100% entries
# python make_table.py file_1,file_2,file_3 -entry 100 // do 100 entries
# python make_table.py file_1,file_2,file_3 -threshold 2 // do entries that occurs at least 2 times

import os, sys, operator, math, copy, glob

percentage = False
threshold = -1
entries = 1e20

file_ = sys.argv[1]
option = sys.argv[2]
number = sys.argv[3]

if option.find("portion")>0:
	percentage = True
	entries = int(number)
if option.find("entry")>0:
	entries = int(number)
if option.find("threshold")>0:
	threshold = int(number)

files = glob.glob(file_ + "/*.block")

dic = []
dic.append({})
dic.append({})
dic.append({})
times = []
times.append({})
times.append({})
times.append({})

tot = []
tot.append(0)
tot.append(0)
tot.append(0)

f = []
f.append(open("temp_0", 'w'))
f.append(open("temp_1", 'w'))
f.append(open("temp_2", 'w'))

f_temp = open("dont_like.txt", 'aw')
f_temp2 = open("do_like.txt", 'aw')

def calc(filename):
	lines = open(filename).readlines()
	r = 0
	for i in range(len(lines)):
		s = lines[i]
		temp = s.split(": ")
		comp = int(temp[0])
		keys = temp[1].split("-2")
		key = keys[0] + "-2"
		if (key in dic[comp]):
			dic[comp][key] += int(keys[1])
			times[comp][key] += 1
		else:
			dic[comp][key] = int(keys[1])
			times[comp][key] = 1
		tot[comp] +=  1
		r += int(keys[1])
	return r

rr = 0
for i in range(len(files)):
	rr += calc(files[i])
print "total run length %s"%(rr)

f_size = open("symbol_table_size.txt", "w")
table_size = 0
dic_for_sort = copy.deepcopy(dic)
for i in range(3):
	gain1 = 0
	for k in dic[i].keys():
		#dic_for_sort[i][k] -= 2* times[i][k]
		#if i == 0:
		#	dic_for_sort[i][k] -= 2* times[i][k]			
		prob = times[i][k]*1.0/tot[i]
		entropy = math.ceil(-math.log(prob, 2))
		bits = dic_for_sort[i][k]/times[i][k]
		dic_for_sort[i][k] -= entropy*times[i][k]
		if times[i][k] == 1:
			del dic_for_sort[i][k]
			continue
		elif entropy >= bits:
			del dic_for_sort[i][k]
			f_temp.write(str(i) + ":[" + k + "] x " + str(times[i][k]) + "(" + str(entropy) + ") " + str(bits) + "x \n")
			continue
		elif dic_for_sort[i][k] <= 0:
			del dic_for_sort[i][k]
			f_temp.write(str(i) + ":[" + k + "] x " + str(times[i][k]) + "(" + str(entropy) + ") " + str(bits) + "v \n")
			continue
		gain1 += dic_for_sort[i][k]
	a = sorted(dic_for_sort[i].iteritems(), key=operator.itemgetter(1), reverse=True)
	temp_c = 0
	f_list = []
	gain = 0
	max_ = len(a)
	if percentage:
		upper_bound = min(max_, entries*max_/100)
	else:
		upper_bound = min(max_, entries)
			
	for j in range(upper_bound):
#		print "bits :", a[j][1]/times[i][a[j][0]], "gain: ", a[j][1], "times: ", times[i][a[j][0]], "run block: ", a[j][0]
		if times[i][a[j][0]] > threshold:     # only consider the block occurs more than threshold times
			temp_c += times[i][a[j][0]]
			prob = times[i][a[j][0]]*1.0/tot[i]
			entropy = math.ceil(-math.log(prob, 2))
			gain += a[j][1]
			f_list.append((a[j][0], times[i][a[j][0]]))
			f_temp2.write(str(i) + ":[" +str(a[j][0]) + "] x " + str(times[i][a[j][0]]) + "(" + str(entropy) + ") " + str(dic[i][a[j][0]]/times[i][a[j][0]]) + "\n")
#			a[j][1]/times[i][a[j][0]]
	print gain1, gain, tot[i]
	default_times = max(1, tot[i] - temp_c)
#	print "gain=", gain, "loss=", default_times, "diff (B)=", (gain-default_times)/8.0
#	print f_list
	f_list.append(('-1 -2', default_times))
	gain1 -= default_times
	gain -= default_times
	print gain1, gain, tot[i]
	a = sorted(f_list, key=operator.itemgetter(1), reverse=True)
	f[i].write(str(len(f_list)) + " " + str(a.index(('-1 -2', default_times))) + "\n")
	for j in range(len(a)):
#		print a[j][1], a[j][0]
		temp = a[j][0].split("-2")
		f[i].write(str(a[j][1]) + " " + temp[0] + "-2 \n")
	f[i].close()
#	print "python ../huff_coding/prob_to_table.py temp_" + str(i) + " symbol_table" + str(i) + ".txt"
	os.system("python prob_to_table.py temp_" + str(i) + " symbol_table" + str(i) + ".txt")
	f_dict = open("symbol_table" + str(i) + ".txt").readlines()
	for j in range(1, len(f_dict)):
		symbol_bits = int(f_dict[j].split(" ")[0])
		run_length_str = f_dict[j][f_dict[j].find(" ") + 1:-2]
		if run_length_str in dic[i]:
			run_length_bits = dic[i][run_length_str]/times[i][run_length_str]
		else:
#			print "not found" + run_length_str
			run_length_bits = 0
#		print run_length_str, ":", run_length_bits, symbol_bits
		table_size += symbol_bits + run_length_bits
f_size.write(str(table_size/8.0))
f_temp.close()
f_temp2.close()
