import sys
import os
import random
import math
import json
import requests
from lxml import html
from lxml import etree


#http://www.health.govt.nz/your-health/conditions-and-treatments/diseases-and-illnesses
baseURL  = "http://www.mayoclinic.org"

def getBasedURLS(url):
	r = requests.get(url)
	tree = html.fromstring(r.text)
	m = tree.xpath('//div[@id="index"]/ol/li/a')
	urls = map(lambda x: x.attrib['href'], m)
	# urls = map(lambda x: x.text_content(), m)
	# print urls
	return urls


def getSicknessData(urls):
	data = []

	for url in urls[6:]:
		sickness = {}
		r = requests.get("http://www.health.govt.nz/" + url)
		tree = html.fromstring(r.text)

		sickness["title"] = tree.xpath('//div[@class="panel-pane pane-page-title even"]/div/h1')[0].text_content()
		sickness["summary"] = tree.xpath('//p[@class="intro-text"]')[0].text_content()
		summaryTabElement = tree.xpath('//dic[@class="summary"]')
		if len(summaryTabElement) == 0:
			sickness["summaryBodyHtml"] = etree.tostring(tree.xpath('//div[@class="field field-name-body field-type-text-with-summary field-label-hidden"]')[0])
			sickness["summaryBody"] = tree.xpath('//div[@class="field field-name-body field-type-text-with-summary field-label-hidden"]')[0].text_content()
		
		#has tabs
		else:
			sickness["summaryBodyHtml"] = etree.tostring(tree.xpath('//div[@class="field field-name-body field-type-text-with-summary field-label-hidden"]')[0])
			sickness["summaryBody"] = tree.xpath('//div[@class="field field-name-body field-type-text-with-summary field-label-hidden"]')[0].text_content()

		summaryTabElement = tree.xpath('//dic[@class="summary"]')


		exit()


# from these pages: http://www.mayoclinic.org/diseases-conditions/migraine-headache/home/ovc-20202432
def extractDataFromPage2(tree):
	# r = requests.get(baseURL + url)	
	# tree = html.fromstring(r.text)

	pageData = {}
	pageData["title"] = tree.xpath('//h1/a')[0].text_content()

	menuLinks = tree.xpath('//div[@class="row"]/ul/li/a')
	# urls = map(lambda x: (x.text_content().strip(),  x.attrib['href']) , menuLinks)
	urls = dict(map(lambda x: (x.text_content().strip(),  x.attrib['href']) , menuLinks))

	definitionURL = urls.get("Overview")
	symptomsURL = urls.get("Symptoms & causes")
	causesURL = urls.get("Symptoms & causes")
	treatmentURL = None
	
	if len(tree.xpath('//a[@class="ico-treatment"]')) > 0:
		treatmentURL = tree.xpath('//a[@class="ico-treatment"]')[0].attrib['href']

	pageData["definition"] = getBodyDataFromPage2( definitionURL )
	pageData["treatment"] = getBodyDataFromPage2( treatmentURL )
	pageData["symptoms"] = getBodyDataFromPage2_Mod( symptomsURL, "Symptoms" )
	pageData["causes"] = getBodyDataFromPage2_Mod( symptomsURL, "Causes" )
	pageData["prevention"] = None

	return pageData


def getBodyDataFromPage2(url):
	if url == None:
		return None

	r = requests.get(baseURL + url)	
	tree = html.fromstring(r.text)

	bodyText = tree.xpath('//div[@class="content"]/div')[1]
	bodyText = map(lambda x: x.text_content().strip(), bodyText)
	bodyText = filter(lambda x: x != "", bodyText)

	if "care at Mayo Clinic" in bodyText[-1]:
		del bodyText[-1]

	return bodyText	

def getBodyDataFromPage2_Mod(url, type):
	if url == None:
		return None
	
	r = requests.get(baseURL + url)	
	tree = html.fromstring(r.text)

	bodyText = tree.xpath('//div[@class="content"]/div')[1]
	bodyText = map(lambda x: (x.tag, x.text_content().strip()), bodyText)
	bodyText = filter(lambda x: x[1] != "", bodyText)

	groupedSections = groupSections(bodyText)

	return groupedSections.get(type)


def groupSections(bodyText):
	out = {}
	currentSection = None
	currentLines = []

	for b in bodyText:
		if(b[0] == "h3"):
			if(currentSection != None):
				out[currentSection] = currentLines
				currentLines = []
			currentSection = b[1]
		else:
			currentLines.append(b[1])

	out[currentSection] = currentLines

	return out


# for these pages: http://www.mayoclinic.org/diseases-conditions/achilles-tendinitis/basics/definition/con-20024518
def extractDataFromPage1(tree):
	# r = requests.get(baseURL + url)	
	# tree = html.fromstring(r.text)

	pageData = {}
	pageData["title"] = tree.xpath('//div[@class="headers v2 lg"]/h1')[0].text_content()

	menuLinks = tree.xpath('//div[@id="main_0_left1_0_tertiarynav"]/ol/li/a')
	urls = dict(map(lambda x: (x.text_content().strip(),  x.attrib['href']) , menuLinks))

	definitionURL = urls.get("Definition")
	symptomsURL = urls.get("Symptoms")
	causesURL = urls.get("Causes")
	preventionURL = urls.get("Prevention")
	treatmentURL =  urls.get("Treatments and drugs")

	pageData["definition"] = getBodyDataFromPage1( definitionURL )
	pageData["symptoms"] = getBodyDataFromPage1( symptomsURL )
	pageData["causes"] = getBodyDataFromPage1( causesURL )
	pageData["prevention"] = getBodyDataFromPage1( preventionURL )
	pageData["treatment"] = getBodyDataFromPage1( treatmentURL )

	return pageData

def getBodyDataFromPage1(url):
	if url == None:
		return None

	r = requests.get(baseURL + url)	
	tree = html.fromstring(r.text)

	bodyText = tree.xpath('//div[@id="main-content"]/p | //div[@id="main-content"]/ul')
	bodyText = map(lambda x: x.text_content().strip(), bodyText)

	toRemove = ["Tests and diagnosisAlternative medicine", "DefinitionCauses" , "ShareTweet", "Symptoms", "Causes", "Definition", "SymptomsRisk factors", "Lifestyle and home remedies", "Tests and diagnosisLifestyle and home remedies", "Coping and support"]
	bodyText = filter(lambda x: x not in toRemove , bodyText)
	return bodyText

def saveToJSON(data, outfile):
	with open(outfile, 'w') as outfile:
		json.dump(data,outfile ,indent=4)

	# print json.dumps(data,indent = 4)



def scrapePage(url):
	r = requests.get(baseURL + url)	
	tree = html.fromstring(r.text)

	bodyText = tree.xpath('//div[@class="breadcrumbs"]')

	if len(bodyText) == 0:
		return extractDataFromPage1(tree)
	elif len(bodyText) == 2:
		return extractDataFromPage2(tree)
	else:
		print "PROBLEM"
		exit()


def scrapeAll(start, end):

	data = []
	for i in range(start,end):
		ch = chr(ord('A') + i)
		urls = getBasedURLS("http://www.mayoclinic.org/diseases-conditions/index?letter=" + ch)

		for url in urls:
			print url
			d = scrapePage(url)
			print d["title"]

			data.append(d)

		saveToJSON(data, "./data/" + ch + ".json")
		data = []


if __name__ == '__main__':

	# scrapePage("/diseases-conditions/anaphylaxis/home/ovc-20307210")
	data =  scrapeAll( int(sys.argv[1]) , int(sys.argv[2]))
	# saveToJSON(data, "data.json")

	# scrapePage("/diseases-conditions/achilles-tendinitis/basics/prevention/con-20024518")

	# urls = getBasedURLS("http://www.mayoclinic.org/diseases-conditions/index?letter=A")
	# getSicknessData(urls)

	# extractDataFromPage("")

	# pageData = extractDataFromPage1("/diseases-conditions/achilles-tendinitis/basics/definition/con-20024518")
	# pageData = extractDataFromPage2("/diseases-conditions/obsessive-compulsive-disorder/home/ovc-20245947")

	# saveToJSON(pageData)