import sys
import os
import random
import math
import json
import requests
import re
import string
from lxml import html
from lxml import etree
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
from retrieval import Retrieval
import numpy as np

retval = Retrieval()

def readTestData(filename):
	data = []
	with open(filename) as data_file:
		next(data_file)
		for line in data_file:
			splt = line.strip().split('\t')
			data.append(splt)

	return data

def findRank(results, goldIllness):
	rank = 1

	for r in results:
		if goldIllness.lower() == r[0]["title"].lower():
			return rank
		rank += 1

	print "Can't find " + goldIllness
	exit()

	return -1

def evalData(testData):

	ranks = []

	for d in testData:
		symp = d[2]
		illness = d[3]
		results = retval.retreive(symp,False)

		rank = findRank(results,illness)
		ranks.append(rank)
		print str(rank) + "\t" + illness

	averageRanks = float(sum(ranks)) / float(len(ranks))
	print "Mean Rank: " + str(averageRanks)

	reciprocalRanks = map(lambda r: 1/float(r), ranks)
	meanReciprocalRanks =  sum(reciprocalRanks) / len(reciprocalRanks)
	print "Mean Reciprical Rank: " + str(meanReciprocalRanks)

def evalData2(testData):

	ranks = []

	for priorWeight in np.arange(0.0, 1.05, 0.05):
		for d in testData:
			symp = d[2]
			illness = d[3]
			results = retval.retreive3(symp, priorWeight)

			rank = findRank(results,illness)
			ranks.append(rank)

		meanRank = float(sum(ranks)) / float(len(ranks))
		
		reciprocalRanks = map(lambda r: 1/float(r), ranks)
		meanReciprocalRank =  sum(reciprocalRanks) / len(reciprocalRanks)

		print str(priorWeight) + "\t" + str(meanRank) + "\t" + str(meanReciprocalRank)	


def tokenize(strr):
	wordnet_lemmatizer = WordNetLemmatizer()
	strr = word_tokenize(strr)
	strr = map(lambda x: wordnet_lemmatizer.lemmatize(x).lower(), strr)
	punctuation = set(string.punctuation) | set(["''", "``", "--", "..."])
	strr = filter(lambda x: x not in punctuation and x not in stopwords.words('english'), strr)
	return strr

def tokenize2(strr):
	wordnet_lemmatizer = WordNetLemmatizer()
	strr = re.sub('[^a-zA-Z0-9-_.\s]', ' ', strr)
	strr = re.sub('\s+', ' ', strr).strip()
	strr = word_tokenize(strr)
	strr = map(lambda x: wordnet_lemmatizer.lemmatize(x).lower(), strr)
	strr = filter(lambda x: x not in stopwords.words('english'), strr)
	return strr

if __name__ == '__main__':

	data = readTestData("sympData.tsv")
	evalData2(data)	

	# strr = "Hello! My name is/Fadi [stupid face jhn]-don't  cough bitch"

	# print tokenize(strr)
	# print tokenize2(strr)
