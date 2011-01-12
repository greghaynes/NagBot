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

	def handlePublicMessage(self, sender, receiver, mesage):
		pass
		

