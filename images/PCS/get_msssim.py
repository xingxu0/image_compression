import os, commands
# a is raw, b is transcoded
def get_msssim(a, b):
	s = commands.getstatusoutput("identify %s"%(a))
	s_ = s[1].split(" ")
	reso = s_[2].split("x")
	i = os.getpid()
	commands.getstatusoutput("ffmpeg -i %s -pix_fmt yuv420p %s.yuv"%(a, "temp_raw_"+str(i)))
	commands.getstatusoutput("ffmpeg -i %s -pix_fmt yuv420p %s.yuv"%(b, "temp_coded_"+str(i)))
	commands.getstatusoutput("/home/xing/vqmt/VQMT/build/bin/Release/vqmt %s %s %s %s 1 1 %s MSSSIM"%("temp_raw_"+str(i)+".yuv", "temp_coded_"+str(i)+".yuv", reso[0], reso[1], "result_"+str(i)))
	c = commands.getstatusoutput("cat %s"%("result_"+str(i)+"_msssim.csv"))
	r = float(c[1].split(",")[3])
	commands.getstatusoutput("rm %s %s %s"%("temp_raw_"+str(i)+".yuv", "temp_coded_"+str(i)+".yuv", "result_"+str(i)+"_msssim.csv"))
	return r
