import os

for i in range(1, 11):
	os.system("jpegtran -encode ../../../image_compression_github/image_compression/tbl_600_q75_1_9 ../../images/10_pic_600/" + str(i) + ".jpg temp.jpg")
	os.system("jpegtran -decode ../../../image_compression_github/image_compression/tbl_600_q75_1_9 temp.jpg " + str(i) + "_out.jpg")
