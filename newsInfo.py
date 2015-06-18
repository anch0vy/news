#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import logging
import time
import re
import datetime
import pickle
from xml.etree.ElementTree import parse as xmlParse
from tf import extractKeyword

newsRssList = [
(u'主要' 		,'main'		,'http://news.livedoor.com/topics/rss/top.xml'		,tuple()								),
(u'国内' 			,'dom'		,'http://news.livedoor.com/topics/rss/dom.xml'		,('4','1')							),
(u'海外' 		,'world'	,'http://news.livedoor.com/topics/rss/int.xml'		,('3','44','42')					),
(u'IT 経済' 		,'eco'		,'http://news.livedoor.com/topics/rss/eco.xml'		,('2','12','31','29','201','210')	),
(u'芸能'		,'ent'		,'http://news.livedoor.com/topics/rss/ent.xml'		,('10','49','214','217')			),
(u'スポーツ' 	,'sports'	,'http://news.livedoor.com/topics/rss/spo.xml'		,('504','503','507','509','510','36','527','21','22','530')),
(u'映画' 		,'52'		,'http://news.livedoor.com/rss/summary/52.xml'		,tuple()								),
(u'グルメ' 		,'gourmet'	,'http://news.livedoor.com/topics/rss/gourmet.xml'	,tuple()								),
(u'女子' 		,'love'		,'http://news.livedoor.com/topics/rss/love.xml'		,tuple()								),
(u'トレンド' 	,'trend'	,'http://news.livedoor.com/topics/rss/trend.xml'	,tuple()								),
]

rssInfoList = ['language','title','link','generator','description','lastBuildDate']
articleInfoList = ['title','link','description','mobile','pubDate','guid']



def getitems(xml,items):
	ret = {}
	for item in items:
		try:
			ret[item] = xml.find(item).text
		except:
			ret[item] = None
	return ret


def getNewsInfo():
	newsInfos = []
	for rss_title,categoryName,rssUrl,relatedcategoryName in newsRssList:
		xmlRss = xmlParse(urllib2.urlopen(rssUrl))
		xmlRoot = xmlRss.getroot()
		xmlChannel = xmlRoot.find('channel')
		rssInfoDict = getitems(xmlChannel,rssInfoList)
		articles = []
		with open('pickles/%s.pickle'%categoryName,'r') as f:
			tf = pickle.load(f)
		for xmlArticle in xmlChannel.iter('item'):
			article = getitems(xmlArticle,articleInfoList)
			id = int(article['link'].split('detail/')[-1].replace('/',''))
			article['description'] = article['description'].replace(u'ざっくり言うと\n    <br />','')
			osusume = tf.search(extractKeyword(article['title']))[:3]
			article['osusume'] = [(score,'http://news.livedoor.com/article/detail/%d/'%_id,title) for (score,_id,title) in osusume if _id != id ]
			articles.append(article)
		newsInfos.append((rss_title,rssInfoDict,articles))
	return newsInfos

if __name__ == '__main__':
	getNewsInfo()