#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division 
import math
import sys
import os
import time
import MeCab
import MySQLdb
import pickle
from glob import glob

tagger = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')


def extractKeyword(text):
    '''return splited text by noun'''
    # tagger = MeCab.Tagger('')
    if type(text) == str:
        node = tagger.parseToNode(text)
    else:
        node = tagger.parseToNode(text.encode('utf-8','ignore'))
    keywords = []
    while node:
        if "名詞" not in node.feature:
            node = node.next
            continue
        splited = node.feature.split(',')
        if splited[0] == "名詞" and splited[1] != "数":
            try:
                tmp = splited[6]
                if '*' in tmp:
                    keywords.append(node.surface)
                else:
                    keywords.append(tmp)
            except IndexError:
                keywords.append(node.surface)
            except:
                print '[!]bug'
        node = node.next
    return keywords


class tfidf:
    def __init__(self):
        print '[!]start set tf',
        t = time.time()
        self.weighted = False
        self.documents = []
        self.corpus_dict = {}


    def addDocument(self, doc_name, articleid , list_of_words):
        # building a dictionary
        doc_dict = {}
        for w in list_of_words:
            doc_dict[w] = doc_dict.get(w, 0.) + 1.0
            self.corpus_dict[w] = self.corpus_dict.get(w, 0.0) + 1.0

        # normalizing the dictionary
        length = float(len(list_of_words))
        for k in doc_dict:
            doc_dict[k] = doc_dict[k] / length

        # add the normalized document to the corpus
        self.documents.append([doc_name,articleid, doc_dict])

    def similarities(self, list_of_words):
        """Returns a list of all the [docname, similarity_score] pairs relative to a list of words."""
        # building the query dictionary
        query_dict = {}
        for w in list_of_words:
            query_dict[w] = query_dict.get(w, 0.0) + 1.0

        # normalizing the query
        length = float(len(list_of_words))
        for k in query_dict:
            query_dict[k] = query_dict[k] / length

        # computing the list of similarities
        sims = []
        scores = []
        for doc in self.documents:
            score = 0.0
            doc_dict = doc[2]
            for k in [x for x in query_dict if x in doc_dict]:
                score += (query_dict[k] + doc_dict[k]) / self.corpus_dict[k]
            if score:
                sims.append((score,doc[1],doc[0]))
                scores.append(score)
        return sims,max(scores),min(scores)

    def search(self,querys):
        tmp,smax,smin = self.similarities(querys)
        stand = (smax + smin*9)/10
        ret =[(a,b,c) for (a,b,c) in tmp if a>stand]
        ret.sort(reverse = True)
        ret = map(lambda (score,id,text):(score ,id, text.decode('utf-8')),ret[:3])
        return ret