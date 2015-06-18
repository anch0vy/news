#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import time
import MySQLdb
import pickle
from flask import Flask , render_template , request , redirect , url_for , session , send_from_directory
from newsInfo import getNewsInfo
from tf import extractKeyword



app = Flask(__name__, static_url_path='')

@app.route('/static/<path:path>')
def static_serve(path):
	return send_from_directory('static',path)

@app.route('/')
@app.route('/home')
def home():
	print '[*]welcom home',
	t=time.time()
	while True:
		try:
			newsInfos = pickle.load(open('pickles/news.pickle'))
			break
		except IOError:
			continue

	print time.time()-t
	return render_template('home.html',newss=newsInfos)


if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0')