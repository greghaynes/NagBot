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
	"""Sends nags to victims"""
	def __init__(self, bot):
		self.bot = bot
		self.victims = {}

	def addVictim(self, victim):
		try:
			cur_victims = self.victims[victim.keyword]
			cur_victims.append(victim)
		except KeyError:
			self.victims[victim.keyword] = [victim]

	def fromString(self, string):
		self.victims = json.JSONEncoder().encode(string)

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

class NagController(object):
	"""Manages commands to nagbot"""
	def __init__(self, bot):
		self.bot = bot

class NagBotMessageHandler(object):
	def __init__(self, bot):
		self.bot = bot
		self.bot_re = re.compile('^' + bot.nickname)

	def handleMessage(self, sender, receiver, message):
		if receiver == self.bot.nickname or self.bot_re.match(message):
			"""Message to the bot"""
			message = message[message.find(' ')+1:]
			handleMessageToBot(sender, message)
		else:
			handlePublicMessage(sender, message)

	def handleMessageToBot(self, sender, message):
		pass

	def handlePublicMessage(self, sender, mesage):
		pass
		

class NagBot(irc.IRCClient):
	"""A bot that sends notifications based on irc message regexes"""
	nickname = "nagbot"

	def __init__(self):
		self.message_handler = NagBotMessageHandler(self)

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

	def irc_PRIVMSG(self, prefix, params):
		self.message_handler.handleMessage(prefix, params[0], params[1])

class NagBotFactory(protocol.ClientFactory):
	protocol = NagBot
	channels = ('#nagbot',)

	def __init__(self, configpath):
		self.config = ConfigParser.ConfigParser()
		self.config.read(configpath)
	
	def clientConnectionFailed(self, connector, reason):
		print "Connection failed:", reason
		reactor.stop()

if __name__ == '__main__':
	# create factory protocol and application
	try:
		f = NagBotFactory('test.conf')
	except IndexError:
		print 'Supply the path to a valid config file as an argument'
	else:
		reactor.connectTCP("irc.cat.pdx.edu", 6667, f)
		reactor.run()

