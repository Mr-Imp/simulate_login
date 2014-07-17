# -*- coding:utf8 -*-
from __future__ import division
import httplib2
import json
import re
from PIL import Image
from StringIO import StringIO
import string
from random import choice
import os
import ImageFilter
import ImageEnhance
from setting import DIC
import urllib
import rsa
import binascii


h = httplib2.Http()
h.follow_redirects = False

class simulate_login():
	def __init__(self):
		#self.base = '/home/xx/xiaoxi/course/image/'
		self.header = {'Accetp':'image/webp,*/*;q=0.8', \
		'Accept-Language':'zh-CN,zh;q=0.8', \
		'Connection':'keep-alive', \
		'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.114 Safari/537.36'}
		self.main_url = 'http://curriculum.hust.edu.cn/'
		self.image_url = 'http://curriculum.hust.edu.cn/imageensureAction.do'
		self.login_url = 'http://curriculum.hust.edu.cn/userLoginAction.do'
		#self.filename = ''.join([choice(string.ascii_letters) for i in range(4)])+'.jpg'
		#os.system(r'touch %s'%(self.base+self.filename))
		self.s = 0
		#left-side-start-px
		self.w = 13
		#divided-image-width-px
		self.h = 18
		#image-height-px
		self.t = 0
		#top-side-start-px
		self.uname = 'u201216223'
		self.passwd = '13801399424'

	def GetCookie(self):
		main_url = self.main_url
		image_url = self.image_url
		login_url = self.login_url
		#path = self.base+self.filename
		header = self.header
		response,content = h.request(main_url,headers = header)
		set_cookie = response['set-cookie']
		cookie = set_cookie.replace(' Path=/,','').replace('; path=/','')
		print(cookie)
		#print content
		father = re.findall("doSubmit.+'",content)
		key = father[0].split("'")[1]
		#print key
		header['Cookie'] = cookie
		header['Cache-Control'] = 'max-age=0'
		response1,content1 = h.request(image_url,headers = header)
		im = Image.open(StringIO(content1))
		#im.save(path,'JPEG')
		#return cookie
		randnum = self.ImageToCode(im)
		print randnum
		if randnum and len(randnum) == 4:
			imageensure = self.image_url+'?randString='+str(randnum)
			header = self.header
			header['Cookie'] = cookie
			response,content = h.request(imageensure,headers = header)
			if content == 'false':
				return 'Identifying code distinguished fail!'
			else:
				rsapubkey = int(key,16)
				pubkey = rsa.PublicKey(rsapubkey,65537)
				uname = binascii.b2a_hex(rsa.encrypt(self.uname,pubkey))
				passwd = binascii.b2a_hex(rsa.encrypt(self.passwd,pubkey))
				header = self.header
				header['Cookie'] = cookie
				data = {'loginId':self.uname, \
				'_loginId':uname, \
				'upassword':self.passwd, \
				'_upassword':passwd, \
				'randnumber':randnum}
				header['Cache-Control'] = 'max-age=0'
				header['Content-Type'] = 'application/x-www-form-urlencode'
				header['Referer'] = 'http://curriculum.hust.edu.cn/Main_index.jsp'
				data = urllib.urlencode(data)
				response,content = h.request(login_url,'POST',data,headers = header)
				print response
				print content






	def __ImageManage(self,image):
		'manage the image,size:60x20->52x18,colorful->black&white'
		sharpness = ImageEnhance.Sharpness(image)
		sh_im = sharpness.enhance(1)
		#sh_im.save('0.jpg')
		contrast = ImageEnhance.Contrast(sh_im)
		con_im = contrast.enhance(5)
		#con_im.save('1.jpg')
		con_im = con_im.convert('L')
		#con_im.save('2.jpg')
		con_im = con_im.crop((4,1,56,19))
		#con_im.save('3.jpg')
		return con_im

	def __CodeToNum(self,l):
		code = []
		for i in range(4):
			if len(l[i]) <= 60:
				print len(l[i])
				return False
			elif len(l[i]) <= 90:
				code.append('1')
				continue
			elif len(l[i]) >= 110:
				code.append('4')
				continue
			#according to quantity of the image's code to roughly judge the number.
			for j in range(10):
				num = 0
				if j == 1:
					continue
				elif j == 4:
					continue
				stan = DIC[str(j)]
				total = len(stan)
				for k in range(len(stan)):
					try:
						bin = l[i][k]
					except:
						total = len(l[i])
						break
					if stan[k] == bin:
						num += 1
				ratio = num/total
				if ratio >= 0.95:
					code.append(str(j))
					break
			if len(code)-1 == i:
				continue
			else:
				return False
			#compare the code with the standard code detailly.
		result = ''.join(code)
		return result

	def ImageToCode(self,image):
		image = image
		image = self.__ImageManage(image)
		im_new = []
		s = self.s
		h = self.h
		w = self.w
		t = self.t
		for i in range(4):
			im = image.crop((s+i*w,t,s+(i+1)*w,h))
			#im.save(str(i+1)+'.jpg')
			im_new.append(im)
		#divide the image into four parts
		l = [[],[],[],[]]
		for k in range(4):
			im_new[k].save(str(k+1)+'.jpg')
			for i in range(h):
				for j in range(w):
					if im_new[k].getpixel((j,i)) <= 200:
						l[k].append(0)
					else:
						l[k].append(1)
		#transformer the image into 1 & 0 list.0->black pix;1->white pix
		#print l[0]
		for k in range(4):
			r = []
			for i in range(h):
				flag = 0
				for j in range(w):
					if l[k][j+i*w] == 0:
						flag = 1
				if flag == 0:
					r.append(i)
			h = h-len(r)
			while True:
				if r:
					m = r.pop()
					del l[k][m*w:(m+1)*w]
				else:
					break
			#adjust the image's height
			for i in range(w):
				flag = 0
				for j in range(h):
					if l[k][i+j*w] == 0:
						flag = 1
				if flag == 0:
					r.append(i)
			while True:
				if r:
					m = r.pop()
					for i in range(h):
						del l[k][m+(h-i-1)*w]
					w = w-1
					#remember do w-=1 !
				else:
					break
			#adjust the image's width
			#for i in range(h):
				#print(l[k][i*w:(i+1)*w])
			#print l[k]
			#print '\n'
			h = self.h
			w = self.w
			#init the image's height and width
		code = self.__CodeToNum(l)
		return code

	

		
if __name__ == '__main__':
	login = simulate_login()
	#im = Image.open('Tryz.jpg')
	#num = login.ImageToCode(im)
	#print num
	login.GetCookie()
