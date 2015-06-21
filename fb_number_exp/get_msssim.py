import os, commands
# a is raw, b is transcoded
def get_msssim(a, b):
	s = commands.getstatusoutput("identify %s"%(a))
	if len(s)<2:
		return -1
	s_ = s[1].split(" ")
	if len(s_)<3:
		return -1
	reso = s_[2].split("x")
	if len(reso)<2:
		return -1
	i = os.getpid()
	a1 = int(reso[0])/16*16
	a2 = int(reso[1])/16*16
	commands.getstatusoutput("ffmpeg -i %s -s %dx%d -pix_fmt yuv420p %s.yuv"%(a, a1, a2, "temp_raw_"+str(i)))
	commands.getstatusoutput("ffmpeg -i %s -s %dx%d -pix_fmt yuv420p %s.yuv"%(b, a1, a2, "temp_coded_"+str(i)))
	commands.getstatusoutput("/home/xing/vqmt/VQMT/build/bin/Release/vqmt %s %s %d %d 1 1 %s MSSSIM"%("temp_raw_"+str(i)+".yuv", "temp_coded_"+str(i)+".yuv", a1, a2, "result_"+str(i)))
	c = commands.getstatusoutput("cat %s"%("result_"+str(i)+"_msssim.csv"))
	if len(c[1])<4:
		return -1
	r = float(c[1].split(",")[3])
	commands.getstatusoutput("rm %s %s %s"%("temp_raw_"+str(i)+".yuv", "temp_coded_"+str(i)+".yuv", "result_"+str(i)+"_msssim.csv"))
	return r
