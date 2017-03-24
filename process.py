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

def getAllDataFromDir(dir):
	files = os.listdir(dir)
	files = filter(lambda x: ".json" in x, files)

	data = []
	for file in files:
		with open(dir+file) as data_file:    
			data.extend(json.load(data_file))

	# print "Num of diseases: " + str(len(data))
	return data

# remove duplicates
def reduce(data):
	dic = {}

	for d in data:
		dic[d["title"]] = d

	out = map(lambda x: dic[x], dic.keys())
	out = sorted(out, key=lambda x: x["title"])

	# print "Num of diseases: " + str(len(out))
	return out

def cleanData(data):

	for d in data:
		for key in ["definition", "causes", "symptoms", "treatment", "prevention"]:
			if d[key] != None:
				d[key] = filter(lambda x: not isHtml(x), d[key])
				d[key] = map(lambda x: clean(x), d[key])

	return data

def isHtml(string):
	return ( "$(" in string or ".createExperiences" in string)

def clean(string):
	# string =  string.replace("  ", " ")
	string = re.sub(' +',' ', string)
	string = re.sub('\r','', string)
	string = re.sub('\n','.', string)
	string = re.sub('\.+','. ', string)
	string = re.sub(' +',' ', string)
	return string

def addTokens(data):
	vocab = []

	for d in data:
		d["tokens"] = sorted(getTokens(d))

	return data

def getVocab(data):
	vocab = {}
	idCounter = 0
	for d in data:

		for t in d["tokens"]:
			if t not in vocab:
				vocab[t] = idCounter
				idCounter += 1

	print "Vocab size: " + str(len(vocab))
	return vocab


def getDFcounts(data, vocabMap):
	dfCounts = defaultdict(int)

	for d in data:
		for t in set(d["tokens"]):
			dfCounts[vocabMap[t]] += 1

	return dfCounts

def createDocVecs(data, vocabMap, dfCounts):
	numDocs = len(data)

	for d in data:
		docVec = defaultdict(float)
		docLen = len(d["tokens"])

		for t in d["tokens"]:
			docVec[vocabMap[t]] += 1.0

		for key in docVec.keys():
			docVec[key] = docVec[key]/numDocs + math.log( float(numDocs) / float(dfCounts[key]) )

		d["docVec"] = docVec
		del d["tokens"]

	return data

def getTokens(jsonObj):
	wordnet_lemmatizer = WordNetLemmatizer()
	allStr = jsonObj["title"]

	for key in ["definition", "causes", "symptoms", "treatment", "prevention"]:
		if jsonObj[key] != None:
			allStr += " " + ' '.join(jsonObj[key])

	allStr = allStr
	allStrTokens = word_tokenize(allStr)
	punctuation = set(string.punctuation) | set(["''", "``", "--", "..."])
	allStrTokens = map(lambda x: wordnet_lemmatizer.lemmatize(x).lower(), allStrTokens)
	allStrTokens = filter(lambda x: x not in punctuation and x not in stopwords.words('english'), allStrTokens)

	return allStrTokens

def saveToJSON(data, outfile):
	with open(outfile, 'w') as outfile:
		json.dump(data,outfile ,indent=4)

def readData(filename):
	with open(filename) as data_file:
		return json.load(data_file)

def printIllnesses():
	data = readData("data.json")
	f = open('illnesses.txt', 'w')

	for d in data:
		f.write(d["title"].encode('utf-8') + "\n")

	f.close()


if __name__ == '__main__':
	printIllnesses()
	# print "Reading data..."
	# data = getAllDataFromDir("./data/")
	# # data = getAllDataFromDir("./testData/")

	# print "Reducing data..."
	# data = reduce(data)

	# print "Cleaning data..."
	# data = cleanData(data)

	# print "Adding tokens..."
	# data = addTokens(data)

	# print "Getting vocab..."
	# vocabMap = getVocab(data)
	# saveToJSON(vocabMap, "vocab.json")

	# print "Calculating DF..."
	# dfCounts = getDFcounts(data, vocabMap)

	# print "Creating doc vecs..."
	# data = createDocVecs(data, vocabMap, dfCounts)

	# saveToJSON(data, "data.json")

