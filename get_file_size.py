import time, os, copy, sys, random, threading, errno, datetime, copy, operator
import BaseHTTPServer, urlparse, cgi,urllib, urllib2
from urllib2 import Request, urlopen, URLError, HTTPError

HOST_NAME = '68.181.99.224'
HOST_PORT = 9999 

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_HEAD(s):
		s.send_response(200)
		s.send_header("Content-type", "text/html")
		s.end_headers()
	def do_GET(self):
		url_content = urlparse.urlparse(self.path)
		query = url_content.query
		path = url_content.path
		args = query.split("&")
		paras = {}
		for i in range(len(args)):
			temp = args[i].split("=")
			if temp[0] == "ppp":
				self.send_response(200)
				self.send_header("Content-type", "text/html")
				self.end_headers()
				self.wfile.write("<html><body>")
				try:
					folder = "/home/xing/research/image_compression_github/image_compression/fb_number_exp/blockwise_ssim/"+temp[1]
					ori_file = temp[1][temp[1].rfind("/")+1:]
					fs_ori = os.path.getsize("/home/xing/research/image_compression_github/image_compression/fb_number_exp/blockwise_ssim/fb_71/"+ori_file)
					fs = os.path.getsize(folder)
				except OSError:
					fs = -1000
					fs_ori = -1000
				self.wfile.write("<b>Image Size:</b>\t" + str(fs/1000) + "KB<br>")
				self.wfile.write("<b>Lossy Saving:</b>\t" + str(int((fs_ori-fs)*100.0/fs_ori)) + "%<br>")
				self.wfile.write("</body></html>")
				break

if __name__ == '__main__':
	server_class = BaseHTTPServer.HTTPServer
	httpd = server_class((HOST_NAME, HOST_PORT), MyHandler)
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	
	httpd.server_close()
