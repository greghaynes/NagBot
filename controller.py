class NagController(object):
	"""Manages commands to nagbot"""
	def __init__(self, bot):
		self.bot = bot
		# command: (handler_func, Reqire Admin)
		self.command_handlers = {
			'quit': (self.command_QUIT, True),
			'createadmin': (self.command_CREATEADMIN, True),
			'part': (self.command_PART, True),
			'rainbow': (self.command_RAINBOW, False),
			'say': (self.command_SAY, True),
			}
		self.admins = {
			'greghaynes': None,
			}

	def respondWith(self, sender, receiver, message):
		if receiver[0] == '#':
			self.bot.msg(receiver, sender.split('!')[0] + ': ' + message)
		else:
			self.bot.msg(sender, message)

	def isAdmin(self, user):
		return user.split('!')[0] in self.admins

	def handleMessageToBot(self, sender, receiver, message, isPrivate):
		split = message.split(' ', 2)
		try:
			cmd = split[0]
		except IndexError:
			pass
			#self.respondWith(sender, receiver, 'No command specified')
			return

		try:
			message = message[message.find(' ')+1:]
		except IndexError:
			message = ''

		try:
			handler = self.command_handlers[cmd.lower()]
			if handler[1] and not self.isAdmin(sender):
				pass
				#self.respondWith(sender, receiver, 'Insufficient permissions')
				return
			else:
				handler[0](sender, receiver, cmd, message, isPrivate)
		except KeyError:
			pass
			#self.respondWith(sender, receiver, 'Invalid command')

	def command_QUIT(self, sender, receiver, cmd, message, isPrivate):
		if message != None:
			self.bot.quit(message)
		else:
			self.bot.quit('Goodbye!')

	def command_CREATEADMIN(self, sender, receiver, cmd, message, isPrivate):
		self.admins[message.split(' ')[0]] = None

	def command_PART(self, sender, receiver, cmd, message, isPrivate):
		if receiver[0] == '#':
			self.bot.leave(receiver, message)
		else:
			self.respondWith(sender, receiver, 'Must be sent in channel desired to part')

	def command_RAINBOW(self, sender, receiver, cmd, message, isPrivate):
		r_msg = ''
		i = 0
		for ch in message:
			r_msg += '\x03' + str((i%11)+2) + ch
			i += 1
		self.bot.say(receiver, r_msg)

	def command_SAY(self, sender, receiver, cmd, message, isPrivate):
		self.bot.say(receiver, message)

