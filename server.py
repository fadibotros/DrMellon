import argparse
import socket
import time
import random
import os, sys
import json
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import urllib
from random import randint
import time
from datetime import datetime
# from db import s3store
from retrieval import Retrieval
from DialogManager import DialogManager
from cgi import parse_header, parse_multipart

# retval = Retrieval()
dm = DialogManager()

class Handler(BaseHTTPRequestHandler):

	def getSessionJson(self, session_id, user_id):

		sessJSON = db.get(session_id)

		# new session
		if sessJSON == None:
			sessJSON = {}
			sessJSON["sessionId"] = session_id
			sessJSON["userId"] = user_id
			sessJSON["startTime"] = str(datetime.now())
			sessJSON["conversation"] = []

		return sessJSON

	# def do_POST(self):
	# 	self.send_response(200)
	# 	self.send_header('Access-Control-Allow-Origin', '*')
	# 	self.end_headers()
		
	# 	message = urllib.unquote_plus(self.path)
	# 	user_id, session_id , user_input_real = message.split('|')

	# 	illness = retval.retreive(user_input_real)[0][0]
	# 	response = "I think you have " + illness
		
	# 	self.wfile.write(response)
		
	# 	return

	def do_POST(self):
		self.send_response(200)
		self.send_header('Access-Control-Allow-Origin', '*')
		self.send_header('Content-Type', 'application/json')
		self.end_headers()
		
		requestJson = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
				
		print json.dumps(requestJson)
		responseJson = dm.getResponse(None,requestJson)
	
		response = json.dumps(responseJson)
		self.wfile.write(response)
		return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':

	server = ThreadedHTTPServer(('', 8080), Handler)
	print 'Starting server, use <Ctrl-C> to stop'
	server.serve_forever()
	
