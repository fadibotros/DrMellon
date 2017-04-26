import sys
import os
import random
import math
import json
import requests
import re
import string
from collections import defaultdict
from scipy.spatial.distance import cosine
import numpy as np
from fuzzywuzzy import fuzz

def bing_search(query):
    url = 'https://api.cognitive.microsoft.com/bing/v5.0/search'
    # query string parameters
    payload = {'q': query}
    # custom headers
    headers = {'Ocp-Apim-Subscription-Key': '39dbfa40ddc94404a58493f315123c5a'}
    # make GET request
    r = requests.get(url, params=payload, headers=headers)
    # get JSON response
    return r.json()

def webSearch(query):
	results = bing_search(query)
	webPageResults = results["webPages"]["value"]
	return webPageResults

if __name__ == '__main__':
	results = bing_search("rugby concussion")

	webPageResults = results["webPages"]["value"]

	titles = map(lambda r: r["name"], webPageResults)

	for t in titles:
		print t