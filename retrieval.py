import sys
import os
import random
import math
import json
import requests
import re
import string
import itertools
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
from scipy.spatial.distance import cosine
import numpy as np
from fuzzywuzzy import fuzz
from webSearch import webSearch

class Retrieval():

	def __init__(self):
		# self.data = self.readData("data.json")
		self.data = self.readData("dataWithPriors2.json")
		self.vocab = self.readData("vocab.json")
		self.data = self.addVectors(self.data,self.vocab)
		self.expandedQueries = {}

	def readData(self,filename):
		with open(filename) as data_file:
			return json.load(data_file)

	def addVectors(self,data, vocab):
		for d in data:
			vec = np.zeros(len(vocab))

			for t in d["docVec"].keys():
				vec[int(t)] = d["docVec"][t]

			d["docVec"] = vec

		return data

	def tokenize(self,strr):
		wordnet_lemmatizer = WordNetLemmatizer()
		strr = re.sub('[^a-zA-Z0-9-_.\s]', ' ', strr)
		strr = re.sub('\s+', ' ', strr).strip()
		strr = word_tokenize(strr)
		strr = map(lambda x: wordnet_lemmatizer.lemmatize(x).lower(), strr)
		strr = filter(lambda x: x not in stopwords.words('english'), strr)
		return strr

	def getTextVec(self, tokens, vocab):
		vec = np.zeros(len(vocab))

		count = 1.0
		for t in tokens:
			if t in vocab:
				vec[vocab[t][0]] += 1
				count += 1.0

		# vec = vec / float(len(tokens))
		vec = vec / count

		for t in tokens:
			if t in vocab:
				vec[vocab[t][0]] += vocab[t][1]

		return vec

	def expandQuery(self,query):
		if query in self.expandedQueries:
			return self.expandedQueries[query]

		webPageResults = webSearch(query)
		titles = map(lambda r: r["name"], webPageResults)
		titlesTokenized = map(lambda t: self.tokenize(t), titles)
		expandedTokens = list(itertools.chain.from_iterable(titlesTokenized))

		self.expandedQueries[query] = expandedTokens
		return expandedTokens

	def retreive(self, query, queryExpansionBool):
		scores = []
		tokens = self.tokenize(query)

		if queryExpansionBool == True:
			# print len(tokens)
			tokens += self.expandQuery(query)
			# print len(tokens)

		queryVec = self.getTextVec(tokens, self.vocab)
		
		for d in self.data:
			score = 1.0 - cosine(d["docVec"], queryVec)
			scores.append((d, score))

		scores = sorted(scores, key = lambda x: -x[1])
		return scores

	def retreive2(self, query, queryExpansionBool, priorWeight):
		scores = []
		tokens = self.tokenize(query)

		if queryExpansionBool == True:
			# print len(tokens)
			tokens += self.expandQuery(query)
			# print len(tokens)

		queryVec = self.getTextVec(tokens, self.vocab)
		
		for d in self.data:
			score = 1.0 - cosine(d["docVec"], queryVec)
			scores.append((d, score))

		scoreSum = sum( map(lambda s: s[1], scores) )
		scores = map(lambda s: (s[0], s[1]/scoreSum), scores)

		# scores = map(lambda s: (s[0], s[1] * s[0]["prior"]), scores)
		scores = map(lambda s: (s[0], (1-priorWeight) * s[1] + priorWeight * s[0]["prior"]), scores)

		scores = sorted(scores, key = lambda x: -x[1])
		return scores

	def retreive3(self,query, expandQueryWeight):
		scores = []
		queryTokens = self.tokenize(query)
		expandedQueryTokens = self.expandQuery(query)

		queryVec = self.getTextVec(queryTokens, self.vocab)
		expandedQueryVec = self.getTextVec(expandedQueryTokens, self.vocab)
		
		for d in self.data:
			queryScore = 1.0 - cosine(d["docVec"], queryVec)
			expandedQueryScore = 1.0 - cosine(d["docVec"], expandedQueryVec)
			scores.append((d, (1.0-expandQueryWeight) * queryScore  + expandQueryWeight * expandedQueryScore))

		scores = sorted(scores, key = lambda x: -x[1])
		return scores


	def getIllnessByName(self, illnessName):
		iName = illnessName.lower()
		scores = []

		for d in self.data:
			if iName == d["title"].lower():
				return d
			simScore = fuzz.partial_ratio(illnessName, d["title"].lower())
			# simScore = fuzz.ratio(illnessName, d["title"].lower())
			scores.append((d,simScore))

		scores = sorted(scores, key = lambda x: -x[1])
		return scores[0][0]

		# if scores[0][1] > 80:
		# 	return scores[0][0]
		# else:
		# 	return None


if __name__ == '__main__':

	retval = Retrieval()

	# while True:
	# 	query = raw_input("illness name: ")

	# 	answers = retval.getIllnessByName(query)
	# 	# print answers

	# 	for a in answers[:20]:
	# 		print a

	# 	print ""

	# query = "Everytime I eat shellfish or seafood, my tongue swells up. My face also swells up. I think I have an allergy"
	# query = "I get distracted easily. I can't focus in class or when I'm studying. I always get distracted."
	# query = "My ears hurt really bad during flights. Especially during takeoff and landing. There is a lot of build up pressure and I have a lot of time to relieve that pressure. Sometimes I get very sharp pains in my ears and get muffled hearing."
	# query = "I have these red bumps on my face. Sometimes I can pop them and white puss comes out."
	# query = "Everytime I eat ice cream or chocolate or drink milk, I get bloated and gassy. Sometimes I get stomach pains."
	# query = "When I eat bread or drink beer, my face gets itchy and sometimes I get bloated."
	# query = "Somtimes I see these weird shapes floating around in my vision. Whenever I look somewhere else, they follow my vision."
	# query = "I drank a lot of beer and wine last night and now I have a really bad headache and I feel very dehydrated and tired"
	# query = "I am sneezing a lot. I can't breath through my nose. I have a really bad headache."

	while True:
		query = raw_input("Your symptoms: ")

		# print retval.expandQuery(query)

		answers = retval.retreive(query,True)
		# answers = retval.retreive2(query,True, 0.35)

		for a in answers[:10]:
			print a[0]["title"] +  "\t" + str(a[1])



