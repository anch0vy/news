#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import MySQLdb
import urllib2
import logging
import time
import re
import datetime
import pickle
import sys
from newsInfo import newsRssList,getNewsInfo
from tf import tfidf as TFIDF
from tf import extractKeyword
DBUSER = DBUSER
DBPASSWORD = DBPASSWORD

newsCategorys = [
('http://news.livedoor.com/topics/category/main/', 'main'),
('http://news.livedoor.com/topics/category/dom/', 'dom'),
('http://news.livedoor.com/topics/category/world/', 'world'),
('http://news.livedoor.com/topics/category/eco/', 'eco'),
('http://news.livedoor.com/topics/category/ent/', 'ent'),
('http://news.livedoor.com/topics/category/sports/', 'sports'),
('http://news.livedoor.com/topics/category/gourmet/', 'gourmet'),
('http://news.livedoor.com/topics/category/love/', 'love'),
('http://news.livedoor.com/topics/category/trend/', 'trend'),
('http://news.livedoor.com/article/category/52/', '52'),
('http://news.livedoor.com/article/category/4/', '4'),
('http://news.livedoor.com/article/category/1/', '1'),
('http://news.livedoor.com/article/category/3/', '3'),
('http://news.livedoor.com/article/category/44/', '44'),
('http://news.livedoor.com/article/category/42/', '42'),
('http://news.livedoor.com/article/category/2/', '2'),
('http://news.livedoor.com/article/category/12/', '12'),
('http://news.livedoor.com/article/category/31/', '31'),
('http://news.livedoor.com/article/category/29/', '29'),
('http://news.livedoor.com/article/category/201/', '201'),
('http://news.livedoor.com/article/category/210/', '210'),
('http://news.livedoor.com/article/category/10/', '10'),
('http://news.livedoor.com/article/category/49/', '49'),
('http://news.livedoor.com/article/category/214/', '214'),
('http://news.livedoor.com/article/category/217/', '217'),
('http://news.livedoor.com/article/category/504/', '504'),
('http://news.livedoor.com/article/category/503/', '503'),
('http://news.livedoor.com/article/category/507/', '507'),
('http://news.livedoor.com/article/category/509/', '509'),
('http://news.livedoor.com/article/category/510/', '510'),
('http://news.livedoor.com/article/category/36/', '36'),
('http://news.livedoor.com/article/category/527/', '527'),
('http://news.livedoor.com/article/category/21/', '21'),
('http://news.livedoor.com/article/category/22/', '22'),
('http://news.livedoor.com/article/category/530/', '530'),
]


def crawlNews(maxpage = 50, daylimit = False):
    logging.basicConfig(filename='crawlNews_%d.log'%int(time.time()), filemode='w', level=logging.DEBUG)
    conn = MySQLdb.connect('192.168.1.2', 'root', 'db[ch[4075', 'data' , charset='utf8')
    cur = conn.cursor()
    for newsCategoryUrl,newsCategoryName in newsCategorys:
        pageNumber = 0
        retryCount = 0
        while maxpage > pageNumber:
            c = 0
            if retryCount == 3:
                pageNumber +=1
                retryCount = 0
            pageNumber +=1
            targetUrl = newsCategoryUrl+'?p=%d'%pageNumber
            try:
                tmp = (year,month,day)
                print targetUrl , '-' , tmp
            except:
                print targetUrl
            try:
                bf = BeautifulSoup(urllib2.urlopen(targetUrl).read())
            except KeyboardInterrupt:
                exit()
            except:
                pageNumber -= 1
                retryCount += 1
                continue
            section = bf.findAll('section',class_='mainSec')[0]
            articleList = section.findAll('ul')[0].findAll('li')
            for article in bf.findAll('div',class_='articleListBody'):
                title = article.h3.text
                short = article.p
                if short is None:
                    short = u''
                else:
                    short = short.text
                articleTime = article.time
                if articleTime is None:
                    pass#use before value
                else:
                    articleTime = article.time.text.replace('\n','')
                    year,month,day = map(int,re.split(u'年|月|日 ',articleTime)[:3])
                    if daylimit and datetime.date.today() > datetime.date(year,month,day):
                        pageNumber += 100000 #trick
                id = int(article.parent['href'].split('detail/')[-1].replace('/',''))
                q = 'INSERT INTO articles (id,title,short,date,category) VALUES (%s,%s,%s,%s,%s)'
                arg = (id,title,short,'%d-%d-%d'%(year,month,day) , newsCategoryName)
                try:
                    cur.execute(q,arg)
                except MySQLdb.IntegrityError:
                    pass
                except KeyboardInterrupt:
                    exit()
            retryCount = 0
            conn.commit()

def maketfpickle():
    conn = MySQLdb.connect('192.168.1.2', DBUSER, DBPASSWORD, 'data' , charset='utf8')
    cur = conn.cursor()
    for title,categoryName,url,relatedcategoryName in newsRssList:
        print categoryName
        categorys = map(repr,(categoryName,) + relatedcategoryName)
        q = 'select * from articles where category = ' + ' or category = '.join(categorys)
        cur.execute(q)
        tfidf = TFIDF()
        while True:
            try:
                f = open('pickles/%s.pickle'%categoryName , 'w')
                break
            except IOError:
                continue
        for n,title,date,short,category in cur:
            title = title.encode('utf-8')
            tfidf.addDocument(title,n,extractKeyword(title))
        pickle.dump(tfidf , f)
        del(tfidf)
        f.close()

if __name__ == '__main__':
    if len(sys.argv)<=1:
        exit()
    op = sys.argv[1]
    if op == 'crawl':
        crawlNews(30, daylimit = False)
    elif op == 'tf':
        maketfpickle()
    elif op == 'article':
        pickle.dump(getNewsInfo(),open('pickles/news.pickle','w'))

