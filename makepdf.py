# -*- coding=utf-8 -*-
# make pdf using given folder which contains page images
# based on pdfgen
# author: q8f13

import os,sys
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.pdfgen import canvas
import shutil


def get_valid_path():
    if len(sys.argv) < 1:
        print('please input target url')
    else:
        pth = sys.argv[1]
    return pth

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

path = get_valid_path()

conpdf(path, False)
