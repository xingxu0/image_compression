import os

for i in range(1, 11):
	os.system("jpegtran -encode ../../tbl_600_q75_1 ../../../../image_compression/images/10_pic_600/" + str(i) + ".jpg temp.jpg")
	os.system("jpegtran -decode ../../tbl_600_q75_1 temp.jpg " + str(i) + "_out.jpg")
