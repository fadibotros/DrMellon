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
		results = retval.retreive(symp,True)

		rank = findRank(results,illness)
		ranks.append(rank)
		print str(rank) + "\t" + illness

	averageRanks = sum(ranks) / len(ranks)
	print "Mean Rank: " + str(averageRanks)

	reciprocalRanks = map(lambda r: 1/float(r), ranks)
	meanReciprocalRanks =  sum(reciprocalRanks) / len(reciprocalRanks)
	print "Mean Reciprical Rank: " + str(meanReciprocalRanks)



if __name__ == '__main__':

	data = readTestData("sympData.tsv")
	evalData(data)	

