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
from scipy.spatial.distance import cosine
import numpy as np

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

	def getTextVec(self, strr, vocab):
		tokens = self.tokenize(strr)
		vec = np.zeros(len(vocab))

		for t in tokens:
			if t in vocab:
				vec[vocab[t]] += 1

		vec = vec / float(len(tokens))
		return vec

	def retreive(self, query):
		scores = []
		queryVec = self.getTextVec(query, self.vocab)
		
		for d in self.data:
			score = cosine(d["docVec"], queryVec)
			scores.append((d["title"], score))

		scores = sorted(scores, key = lambda x: x[1])
		return scores


if __name__ == '__main__':

	retval = Retrieval()

	# query = "Everytime I eat shellfish or seafood, my tongue swells up. My face also swells up. I think I have an allergy"
	# query = "I get distracted easily. I can't focus in class or when I'm studying. I always get distracted."
	# query = "My ears hurt really bad during flights. Especially during takeoff and landing. There is a lot of build up pressure and I have a lot of time to relieve that pressure. Sometimes I get very sharp pains in my ears and get muffled hearing."
	# query = "I have these red bumps on my face. Sometimes I can pop them and white puss comes out."
	# query = "Everytime I eat ice cream or chocolate or drink milk, I get bloated and gassy. Sometimes I get stomach pains."
	# query = "When I eat bread or drink beer, my face gets itchy and sometimes I get bloated."
	# query = "Somtimes I see these weird shapes floating around in my vision. Whenever I look somewhere else, they follow my vision."
	
	while True:
		query = raw_input("Your symptoms: ")

		answers = retval.retreive(query)

		for a in answers[:10]:
			print a
