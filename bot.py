from twisted.words.protocols import irc
from twisted.internet import ssl, reactor, protocol
from twisted.internet.error import DNSLookupError
from twisted.python import log

from nagger import Nagger
from controller import NagController

import sys
import ConfigParser
import re
import json
import random

nicks = open('names.txt')

class NagBotMessageHandler(object):
	def __init__(self, bot):
		self.bot = bot
		self.bot_re = re.compile('^' + self.bot.nickname)
		self.controller = NagController(bot)
		self.nagger = Nagger(bot)

	def handleMessage(self, sender, receiver, message):
		if receiver == self.bot.nickname or self.bot_re.match(message):
			"""Message to the bot"""
			message = message[message.find(' ')+1:]
			self.controller.handleMessageToBot(sender, receiver, message, receiver == self.bot.nickname)
		else:
			self.nagger.handlePublicMessage(sender, receiver, message)

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
		self.say(channel, "\x034Hello!")

	def irc_PRIVMSG(self, prefix, params):
		self.message_handler.handleMessage(prefix, params[0], params[1])

class NagBotFactory(protocol.ClientFactory):
	protocol = NagBot
	channels = ('#cs305',)

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
		for i in range(1):
			reactor.connectSSL("irc.cat.pdx.edu", 6697, f, ssl.ClientContextFactory())
		reactor.run()

