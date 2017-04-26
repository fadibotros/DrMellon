import sys
import os
import random
import math
import json
import requests
import urllib
import re
from lxml import html
from lxml import etree


def saveToJSON(data, outfile):
	with open(outfile, 'w') as outfile:
		json.dump(data,outfile ,indent=4)


def loadJSON(filename):
	with open('data.json') as data_file:    
		return json.load(data_file)

def extractNumbersFromString(str):
	return [int(s) for s in str.split() if s.isdigit()]

def cleanString(txt):
	txt = re.sub('[^a-zA-Z0-9-_.\s]', ' ', txt)
	txt = re.sub('\s+', ' ', txt).strip()
	return txt

def getNumOfComments(illnessName):
	# baseURL = "http://www.medicinenet.com/script/main/srchcont.asp?src=eye+floaters"
	illnessName = cleanString(illnessName)
	baseURL = "http://www.medicinenet.com"
	resultIllnessName = ""
	numComments = 0

	try:
		r = requests.get(baseURL + "/script/main/srchcont.asp?src=" + urllib.quote_plus(illnessName))

		tree = html.fromstring(r.text)

		links = tree.xpath('//div[@class="SearchResults_fmt"]//td/ul/li/a')#.text_content()
		if len(links) == 0:
			return ("",0)

		resultIllnessName = links[0].text_content()
		resultIllnessLink = links[0].attrib['href']
		
		r = requests.get(baseURL + resultIllnessLink)
		tree = html.fromstring(r.text)
		links = tree.xpath('//a[@onclick="wmdTrack(\'pd-view\')"]')
		if len(links) == 0:
			return ("",0)
		commentsStr = links[0].text_content()
		numComments = extractNumbersFromString(commentsStr)[0]
	except requests.exceptions.TooManyRedirects:
		print "Too many directs Error"
		pass

	return (resultIllnessName, numComments)

def addPriors(data):

	for d in data:
		print d["title"]
		resultIllnessName, numComments = getNumOfComments(d["title"])
		print resultIllnessName
		print numComments
		print ""

		d["numComments"] = float(numComments)

	#apply smoothing
	totalComments = sum(map(lambda d: d["numComments"],data)) + len(data)

	for d in data:
		d["prior"] = (d["numComments"] + 1.0) / totalComments

	return data

if __name__ == '__main__':

	data = loadJSON("data.json")
	data = addPriors(data)
	saveToJSON(data,"dataWithPriors.json")
	
	# getNumOfComments("Adult attention deficit hyperactivity disorder ADHD")