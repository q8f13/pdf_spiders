# -*- coding=utf-8 -*-
# sina iask document spider
# based on pdfgen
# author: q8f13

import re,json,os,sys
import urllib.request
from urllib.request import urlopen
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.pdfgen import canvas
import shutil
import time,random

# PAGE = 'http://ishare.iask.sina.com.cn/f/21028483.html'

#  REG_IMG_URL = '"http://gslb.sinastorage.cn.*\d"'
REG_IMG_URL = '"http://swf.ishare.down.sina.com.cn.*\d"'
# REG_IMG_URL = '"http://sinacloud.net.*\d"'
REG_JSON = '{"totalpage".*}'
REG_FNAME = '="fname.*>'
REG_VALID_URL = '^https?:/{2}ishare\.iask\.sina.*'

def get_valid_url():
	url = ""
	is_valid = False
	if len(sys.argv) < 1:
		print('please input target url')
	else:
		is_valid = re.match(REG_VALID_URL, sys.argv[1])
		if bool(is_valid):
			url = sys.argv[1]
		else:
			print("invalid url '%s'" % sys.argv[1])
	return (url,is_valid)
	

# 获取页面中保存的文档信息json
def get_page_json_data(content):
	data_raw = re.search(REG_JSON, content)
	return json.loads(data_raw.group(0))

def get_img_url(content):
	url = re.search(REG_IMG_URL, content).group(0)[1:-1]
	return url

def get_fname(content):
	n = re.search(REG_FNAME, content).group(0)[16:-3]
	return n

# TODO:抓url保存成文件
def download_image_to_file(url, idx, page_section, path):
	url = re.sub('range=.*', 'range={}-{}'.format(page_section[0],page_section[1]), url)
	fpath = '{}{}.jpg'.format(path, idx)
	if os.path.isfile(fpath):
		return
	print('downloading page %s:%s ...' % (idx,url))
	with urlopen(url) as conn:
		data = conn.read()
		f = open(fpath, 'w+b')
		f.write(data)
		f.close()
	# urllib.request.urlretrieve(url, '{}{}.jpg'.format(path, idx))
	time.sleep(random.uniform(1.7,2.2))

def conpdf(path, rmPics = True):
	(w,h) = portrait(A4)
	c = canvas.Canvas('%s.pdf' % path[:-1], pagesize=portrait(A4))
	if not os.path.exists(path):
		print("path %s not found" % path)	
		return
	flist = []
	# for dirpath,dirnames,filenames in os.walk(path):
	# 	filenames = filter(lambda filename:filenames[-4] == '.jpg' , filenames)
	# 	filenames = map(lambda filename:os.path.join(dirpath, filename),filenames)
	# 	flist.extend(filenames)
	for root,dirs,files in os.walk(path):
		for p in files:
			if p[-4:] == '.jpg' or p[-4:] == '.png':
				flist.append(p)
		flist.sort(key=lambda x:int(x[:-4]))
		# sorted(flist, key=lambda x:int(x))
		for ff in flist:
			c.drawImage(root + '//' + ff,0,0,w,h)
			c.showPage()
	c.save()
	if rmPics:
		shutil.rmtree(path)
	# print(flist[0])

###############################

# main:
param_parsed = get_valid_url()
page_url = param_parsed[0]
valid = param_parsed[1]

# quit if invalid url param
if not valid:
	quit()


opener = urllib.request.urlopen(page_url)
content = opener.read().decode('utf-8')

data = get_page_json_data(content)

# 文档页数
totalpage = int(data['totalpage'])
print("total %s pages" % totalpage)

# 分页信息
page_data = data['bytes'].items()
fname = get_fname(content)
print("filename: %s" % fname)

# quit if pdf exist
if os.path.exists(fname):
	print('pdf file already exist')
	quit()

if not os.path.exists(fname[:-4]):
	os.makedirs(fname[:-4])
path = r'./%s/' % fname[:-4]

img_url = get_img_url(content)
print(img_url)

try:
	for p, no in data['bytes'].items():
		download_image_to_file(img_url, p, no, path)
except IOError as e:
	print("Error occurs: %s" % e)
	sys.exit()

conpdf(path)

print("Done. Enjoy")

# print('img url: ', get_img_url(content))

# page_section = page_data['1']
