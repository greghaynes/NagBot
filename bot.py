from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

import sys

class NagBot(irc.IRCClient):
	"""A bot that nags people based on message regexes"""
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
	protocol = NagBot

	def __init__(self, channels):
		self.channels = channels
	
	def clientConnectionFailed(self, connector, reason):
		print "Connection failed:", reason
		reactor.stop()

if __name__ == '__main__':
	# create factory protocol and application
	f = NagBotFactory((sys.argv[1],))
	reactor.connectTCP("irc.cat.pdx.edu", 6667, f)
	reactor.run()

