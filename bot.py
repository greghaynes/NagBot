from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.internet.error import DNSLookupError
from twisted.python import log

import sys
import ConfigParser
import re
import json

class Destination(object):
	"""Base class for destination implementations"""
	def __init__(self):
		pass

	def sendMessage(self, message):
		"""Called when message should be sent to the destination"""
		pass

	def toString(self):
		"""Called to serialize destination"""
		return ''

	def fromString(self):
		"""Called to deserialize destination"""
		pass

class LogDestination(Destination):
	def sendMessage(self, message):
		logging.message(message)	

class Victim(object):
	"""Ties a keyword with dest and handles relevant irc messages
	   A message in the form !<keyword> triggers the nag"""
	def __init__(self, keyword, dest):
		self.keyword = keyword
		self.dest = dest

	def notifyMessage(self, sender, receiver, message):
		"""Called when destination should be notified of message"""
		pass

class Nagger(object):
	def __init__(self, bot):
		self.bot = bot
		self.victims = {}

	def addVictim(self, victim):
		try:
			cur_victims = self.victims[victim.keyword]
			cur_victims.append(victim)
		except KeyError:
			self.victims[victim.keyword] = [victim]

	def handleMessage(self, sender, reciever, message):
		"""Called for each message seen"""
		pass

	def toString(self):
		"""Serialize the nagger"""
		# TODO: We probably dont have to make a copy of state here
		serial_victims = {}
		for key, value in self.victims.items():
			serial_values = []
			for victim in value:
				serial_values.append(victim.dest.toString())
			serial_victims[key] = serial_values
		return json.dumps(serial_victims)

class NagBot(irc.IRCClient):
	"""A bot that sends notifications based on irc message regexes"""
	nickname = "nagbot"

	def connectionMade(self):
		irc.IRCClient.connectionMade(self)

	def connectionLost(self, reason):
		irc.IRCClient.connectionLost(self, reason)

	def signedOn(self):
		"""Called when bot has succesfully signed on to server."""
		for channel in self.factory.channels:
			self.join(channel)

	def joined(self, channel):
		"""This will get called when the bot joins the channel."""
		self.say(channel, "Hello!")

class NagBotFactory(protocol.ClientFactory):
	def __init__(self, configpath):
		self.config = ConfigParser.ConfigParser()
		self.config.read(configpath)
	
	def clientConnectionFailed(self, connector, reason):
		print "Connection failed:", reason
		reactor.stop()

if __name__ == '__main__':
	# create factory protocol and application
	try:
		f = NagBotFactory((sys.argv[1],))
	except IndexError:
		print 'Supply the path to a valid config file as an argument'
	else:
		reactor.connectTCP("irc.cat.pdx.edu", 6667, f)
		reactor.run()

