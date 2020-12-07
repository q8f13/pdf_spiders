# -*- coding=utf-8 -*-
# doc88 spider based on selenium
# author: q8f13
# https://github.com/q8f13
#
# Change Log
# 
# - 2019.7.1
#   Changed scanning method due to update of doc88 website
#   Single page open & capture step no longer needed

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os,sys,re
import base64
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.pdfgen import canvas
import shutil
import contextlib

REG_VALID_URL = '^https?:/{2}www\.doc88\.*'
TEMP_IMG_FOLDER = 'img'

@contextlib.contextmanager
def quitting(thing):
    yield thing
    thing.quit()

# retrive url from cli parameter
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

# combine pictures to pdf
def conpdf(path, filename, rmPics = True):
	(w,h) = portrait(A4)
	c = canvas.Canvas('%s.pdf' % filename, pagesize=portrait(A4))
	if not os.path.exists(path):
		print("path %s not found" % path)	
		return
	flist = []
	for root,dirs,files in os.walk(path):
		for p in files:
			if p[-4:] == '.jpg' or p[-4:] == '.png':
				flist.append(p)
		flist.sort(key=lambda x:int(x[:-4]))
		for ff in flist:
			c.drawImage(root + '//' + ff,0,0,w,h)
			c.showPage()
	c.save()
	if rmPics:
		shutil.rmtree(path)

# validate url
(u,valid) = get_valid_url()

if not valid:
    print("not a valid url %s" % u)
    quit()

# do some preparation
url = u
url_digout_list =[]

# make sure the flash content should be openned correctly
option = webdriver.FirefoxOptions()
option.set_preference("plugin.state.flash", 2)

# create main container
driver = webdriver.Firefox(options=option)
driver.get(url)

# take a break, make sure to tell user make flash plugin automatically enabled
# including expand some folded document
#  raw_input('press Enter to start scanning, make sure you toggled flash on first, and expand all pages of document..\n')
input('press Enter to start scanning, make sure you toggled flash on first, and expand all pages of document..\n')

# find the dom elements
title_block = driver.find_element_by_class_name('doctopic')
title_name = title_block.find_element_by_tag_name('h1').get_attribute('title')
outer_pages = driver.find_elements_by_class_name('outer_page')
# inner_pages = driver.find_elements_by_class_name('inner_page')

page_count = len(outer_pages)
# page_count = len(inner_pages)
count = 0

print('start scanning elements, please scroll down to the page bottom\n')

# retrive flash objects and parameters
# for p in inner_pages:
for p in outer_pages:
    try:
        inner = p.find_element_by_class_name('inner_page')
        pb = p.find_element_by_class_name('page_pb')
        #  obj = WebDriverWait(p, 999).until(
            #  EC.text_to_be_present_in_element(pb, '')
            #  # EC.presence_of_element_located((By.TAG_NAME,'object'))
        #  )
    except Exception as e:
        print(e)
        print('failed on this one :%s' % count)
        continue

    #  swf_url = obj.get_attribute('data')
    #  data_url = obj.find_element_by_name('FlashVars').get_attribute('value')
    #  combined = swf_url + '&' + data_url
    # url_digout_list.append(combined)
    url_digout_list.append(inner)

    count+=1
    # print('page %s: %s' % (count, combined))

# print('scanning done, taking screencaptures of every page, PLEASE DO NOT CLOSE THE BROWSER AUTOMATICALLY POPED\n')

input('press Enter when scanning done and scrolling to bottom')
#  raw_input('press Enter when scanning done and scrolling to bottom')


# open single containers for single page loading and take screenshots
p_count = 0

# make sure there's temp folder
if os.path.exists(TEMP_IMG_FOLDER):
    os.removedirs(TEMP_IMG_FOLDER)

if not os.path.exists(TEMP_IMG_FOLDER):
    os.makedirs(TEMP_IMG_FOLDER)

for pp in url_digout_list:
    canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", pp)
    canvas_png = base64.b64decode(canvas_base64)
    with open(r'./%s/%s.png' % (TEMP_IMG_FOLDER, p_count),'wb') as f:
        f.write(canvas_png)
    #  with quitting(webdriver.Firefox(options = option)) as dri:
        #  dri.implicitly_wait(10)
        #  dri.get(pp)
        #  dri.set_window_size(960,1357)
        #  sleep(2)
        #  dri.save_screenshot('./%s/%s.png' % (TEMP_IMG_FOLDER,p_count))
    p_count+=1

print('combining to pdf file..\n')

# combine images to pdf
conpdf(TEMP_IMG_FOLDER, title_name)

driver.close()
print('crawling done, enjoy!')

