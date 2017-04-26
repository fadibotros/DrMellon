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
		self.data = self.readData("data.json")
		self.vocab = self.readData("vocab.json")
		self.data = self.addVectors(self.data,self.vocab)

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
		strr = word_tokenize(strr)
		strr = map(lambda x: wordnet_lemmatizer.lemmatize(x).lower(), strr)
		punctuation = set(string.punctuation) | set(["''", "``", "--", "..."])
		strr = filter(lambda x: x not in punctuation and x not in stopwords.words('english'), strr)
		return strr

	def getTextVec(self, tokens, vocab):
		vec = np.zeros(len(vocab))

		count = 1.0
		for t in tokens:
			if t in vocab:
				vec[vocab[t]] += 1
				count += 1.0

		# vec = vec / float(len(tokens))
		vec = vec / count
		return vec

	def expandQuery(self,query):
		webPageResults = webSearch(query)
		titles = map(lambda r: r["name"], webPageResults)
		titlesTokenized = map(lambda t: self.tokenize(t), titles)

		return list(itertools.chain.from_iterable(titlesTokenized))


	def retreive(self, query, queryExpansionBool):
		scores = []
		tokens = self.tokenize(query)

		if queryExpansionBool == True:
			# print len(tokens)
			tokens += self.expandQuery(query)
			# print len(tokens)

		queryVec = self.getTextVec(tokens, self.vocab)
		
		for d in self.data:
			score = cosine(d["docVec"], queryVec)
			scores.append((d, score))

		scores = sorted(scores, key = lambda x: x[1])
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

		for a in answers[:10]:
			print a[0]["title"] +  "\t" + str(a[1])

# 25	Common cold
# 489	Stress fractures
# 33	Concussion
# 4	Frostbite
# 1	Eye floaters
# 10	Bruxism (teeth grinding)
# 40	Knee pain
# 1	Hangovers
# 158	Airplane ear
# 1	Eyestrain
# 10	Kidney stones
# 19	Celiac disease
# 3	Lactose intolerance
# 23	Jellyfish stings
# 7	Cold sore

# 6	Common cold
# 32	Stress fractures
# 3	Concussion
# 4	Frostbite
# 1	Eye floaters
# 8	Bruxism (teeth grinding)
# 11	Knee pain
# 2	Hangovers
# 2	Airplane ear
# 1	Eyestrain
# 19	Kidney stones
# 24	Celiac disease
# 1	Lactose intolerance
# 79	Jellyfish stings
# 13	Cold sore

