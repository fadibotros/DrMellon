import argparse
import socket
import time
import random
import os, sys
from retrieval import Retrieval

class DialogManager():

	def __init__(self):
		# self.retval = Retrieval()
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
		card_title = "Hi, I'm doctor Mellon. You can tell me your symptoms and I will try to diagnose you."
		speech_output = "Hi, I'm doctor Mellon. You can tell me your symptoms and I will try to diagnose you."
		reprompt_text = "What can I help you with?"
		should_end_session = False
		return self.build_response(session_attributes, self.build_speechlet_response(
			card_title, speech_output, reprompt_text, should_end_session))

	def stop(self):
		card_title = "Have a nice day!"
		speech_output = "Have a nice day!"
		should_end_session = True
		return build_response({}, build_speechlet_response(
			card_title, speech_output, None, should_end_session))

	def help(self):
		card_title = "What do you want to talk about?"
		speech_output = "Let's have a conversation. What do you want to talk about?"
		reprompt_text = "What do you want to talk about?"
		should_end_session = False
		return build_response({}, build_speechlet_response(
			card_title, speech_output, reprompt_text, should_end_session))

	def on_intent(self,intent_request, session):
		""" Called when the user specifies an intent for this skill """

		print("on_intent requestId=" + intent_request['requestId'] +
			  ", sessionId=" + session['sessionId'])

		intent = intent_request['intent']
		intent_name = intent_request['intent']['name']

		print("*** Intent Name: " + intent_name)

		# Dispatch to your skill's intent handlers
		if intent_name == "HelloIntent":
			return say_hello()
		elif intent_name == "StopIntent":
			return stop()
		elif intent_name == "HelpIntent":
			return help()
		elif intent_name == "RawText":
			return handle_chat(intent_request, session['sessionId'], session['user']['userId'])
		elif intent_name == "definitionIntent":
			return test(intent_request, session['sessionId'], session['user']['userId'])
		else:
			raise ValueError("Invalid intent")	    

	def getResponse(self,sessJSON, requestJSON):

		response = self.say_hello()
		# if event['request']['type'] == "LaunchRequest":
		# 	return say_hello()
		# elif event['request']['type'] == "IntentRequest":
		# 	return on_intent(event['request'], event['session'])
		# elif event['request']['type'] == "SessionEndedRequest":
		# 	return on_session_ended(event['request'], event['session'])
		

		return response
