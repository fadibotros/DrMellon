import argparse
import socket
import time
import random
import os, sys
from retrieval import Retrieval

class DialogManager():

	def __init__(self):
		self.retval = Retrieval()
		self.currentIllness = None
		i =1

	def build_speechlet_response(self,title, output, reprompt_text, should_end_session):
		return {
			'outputSpeech': {
				'type': 'PlainText',
				'text': output
			},
			'card': {
				'type': 'Simple',
				'title': "SessionSpeechlet - " + title,
				'content': "SessionSpeechlet - " + output
			},
			'reprompt': {
				'outputSpeech': {
					'type': 'PlainText',
					'text': reprompt_text
				}
			},
			'shouldEndSession': should_end_session
		}

	def build_response(self, session_attributes, speechlet_response):
		return {
			'version': '1.0',
			'sessionAttributes': session_attributes,
			'response': speechlet_response
		}

	# --------------- Functions that control the skill's behavior ------------------
	def say_hello(self):
		session_attributes = {}
		card_title = "Hi, I'm doctor Mellon. How can I assisst you?"
		speech_output = "Hi, I'm doctor Mellon. How can I assisst you?"
		reprompt_text = "What can I help you with?"
		should_end_session = False
		return self.build_response(session_attributes, self.build_speechlet_response(
			card_title, speech_output, reprompt_text, should_end_session))

	def stop(self):
		output = "Have a nice day!"
		should_end_session = True
		return build_response({}, self.build_speechlet_response(
			output, output, None, should_end_session))

	def help(self):
		output = "How can I assist you ?"
		should_end_session = False
		return build_response({}, self.build_speechlet_response(
			output, output, output, should_end_session))

	def handleDefinitionIntent(self,intentObj):
		illnessName = intentObj["slots"]["Illnesses"]["value"]
		illness = self.retval.getIllnessByName(illnessName)
		self.currentIllness = illness

		output = illness["definition"][0]
		should_end_session = False

		return self.build_response({}, self.build_speechlet_response(
			output, output, output, should_end_session))

	def handleSymptomsIntent(self,intentObj):
		should_end_session = False
		output = None

		# check if user specified an illness
		if "value" in intentObj["slots"]["Illnesses"]:
			illnessName = intentObj["slots"]["Illnesses"]["value"]
			illness = self.retval.getIllnessByName(illnessName)

			output = " ".join(illness["symtopn"][:2])
			should_end_session = False
		elif self.currentIllness != None:
			output = " ".join(self.currentIllness["symtopn"][:2])
		else:
			output = "Sorry I didn't quite understand that..."

		return self.build_response({}, self.build_speechlet_response(
				output, output, output, should_end_session))



	def on_intent(self,intent_request, session):
		""" Called when the user specifies an intent for this skill """

		print intent_request

		intent = intent_request['intent']
		intent_name = intent_request['intent']['name']

		# Dispatch to your skill's intent handlers
		if intent_name == "HelloIntent":
			return say_hello()
		elif intent_name == "StopIntent":
			return self.stop()
		elif intent_name == "HelpIntent":
			return self.help()
		elif intent_name == "RawText":
			return self.handle_chat(intent_request, session['sessionId'], session['user']['userId'])
		elif intent_name == "definitionIntent":
			return self.handleDefinitionIntent(intent_request["intent"])
		else:
			raise ValueError("Invalid intent")	    

	def getResponse(self,sessJSON, requestJSON):

		response = None
		if requestJSON['request']['type'] == "LaunchRequest":
			response = self.say_hello()
		elif requestJSON['request']['type'] == "IntentRequest":
			response = self.on_intent(requestJSON['request'], requestJSON['session'])

		return response
