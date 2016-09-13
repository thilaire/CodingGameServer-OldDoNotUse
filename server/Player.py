import logging
from socketserver import ThreadingTCPServer, BaseRequestHandler
from logging.handlers import RotatingFileHandler
from re import sub
from threading import Event

logger = logging.getLogger()		# general logger ('root')


class connectionError(Exception):
	"""stupid class to manage the errors due to the connection
	"""
	# TODO: Usefull ?
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)



class PlayerSocketHandler(BaseRequestHandler):
	"""
	The request handler class for our server.
	It is instantiated once per connection to the server, ie one per player
	"""
	def handle(self):

		self._player = None
		try:
			# get the name from the client and create the player
			name = self.getPlayerName()
			self._player = Player( name )

			# then, wait for a game
			self.waitForGame()

			while True:
				data = str( self.request.recv(1024).strip(), "utf-8" )
				self._player.logger.debug( "Receive '%s' from player %s (%s)"%( data, self._player.name, self.client_address[0] ))

				if data.startswith("GET_LAB:"):
					#retrieve data command
					print("Not yet implemented...")
					pass

				elif data.startswith("GET_MOVE:"):
					# get move of the opponent
					self._player.opponent.plays()
					self._player.doesnotplay()
					self._player._
					pass

				elif data.startswith("PLAY_MOVE:"):
					# play move
					print("Not yet implemented...")
					pass

				elif data.startswith("DISP_LAB:"):
					# return the labyrinth
					self.request.sendall(b"OK")
					logger.debug("Send OK to player %s (%s)" % (self.playerNameAdress))
					self.request.sendall( str(self._player.game).encode() )
					logger.debug("Send the labyrinth to display to player %s (%s)" % (self.playerNameAdress))

				elif data.startswith("SEND_COMMENT:"):
					# return the labyrinth
					self.request.sendall(b"OK")
					logger.debug("Send OK to player %s (%s)" % (self.playerNameAdress))
					#TODO: send a comment to the game

				else:
					raise connectionError("Bad protocol, command should not start with '"+data+"'")

		except connectionError as e:
			if self._player:
				self._player.logger.error( "Error with %s: '%s'"%(self._player.name, self.client_address[0], e) )
			else:
				logger.error("Error with %s: '%s'" % (self._player.name, self.client_address[0], e))


	def finish(self):
		"""
		Call when the connection is closed
		"""
		if self._player is not None:
			self._player.logger.debug("Connection closed with player "+self.playerNameAdress)
			Player.removePlayer(self._player.name)
			del self._player




	def getPlayerName(self):
		"""
		receive and treat connection to get the player name
		:return:
		the player name
		or raises an exception (connectionError)
		"""
		data = str( self.request.recv(1024).strip(), "utf-8" )
		logger.debug( "Receive: '"+data+"' from client "+self.client_address[0] )
		if not data.startswith("CLIENT_NAME: "):
			raise connectionError( "Bad protocol, should start with CLIENT_NAME: ")

		# check if the player doesn't exist yet
		if data[13:] in Player.allPlayers:
			self.request.sendall( b"A client with the same name ('" + data[13:].encode() + b"') is already connected!" )
			raise connectionError("A client with the same name is already connected: %s (%s)"%( data[13:], self.client_address[0] ))

		# check if the name is valid (20 characters max, and only in [a-zA-Z0-9_]
		name = sub( '\W+', '',data[13:])
		if name != data[13:] or len(name)>20:
			self.request.sendall( b"The name is invalid (max 20 characters in [a-zA-Z0-9_])" )
			raise connectionError("The name '%s' (from %s) is invalid (max 20 characters in [a-zA-Z0-9_])"%( data[13:], self.client_address[0] ))

		# just send back OK
		self.request.sendall(b"OK")
		logger.debug( "Send OK to player %s (%s)"%( name, self.client_address[0]))
		return name


	@property
	def playerNameAdress(self):
		return "%s (%s)"%( self._player.name if self._player is not None else "None", self.client_address[0])



	def waitForGame(self):
		# get the WAIT_GAME message
		data = str(self.request.recv(1024).strip(), "utf-8")
		self._player.logger.debug("Receive '%s' from player %s (%s)" % (data, self._player.name, self.client_address))
		if not data.startswith("WAIT_GAME"):
			raise connectionError( "Bad protocol, should send 'WAIT_GAME' command")

		# just send back OK
		self.request.sendall(b"OK")
		logger.debug("Send OK to player "+self.playerNameAdress )

		# wait for the Game
		self._player._waitingGame.wait()	# WAIT until the event _waitingGame is set by the game.setter of the player (so when the game assigned itself to the game property of a player)
		self._player._waitingGame.clear()	# clear it for the next game...

		# now send the game name
		self.request.sendall( self._player.game.name.encode('utf-8') )
		logger.debug("Send the game name ('%s') to player %s" % (self._player.game.name, self.playerNameAdress ))

		# now send the game sizes
		self.request.sendall( b"%d %d"%(self._player.game.sizeX, self._player.game.sizeY) )
		logger.debug("Send the game size ('%d %d') to player %s" % (self._player.game.sizeX, self._player.game.sizeY, self.playerNameAdress ))



class Player:
	"""
	A Player

	- _logger: a logger, used to log info/debug/errors
	- _name: its name
	- _game: the game it is involved with
	- _waitingGame: an Event used to wait for the game to start (set when a game is set)
	- _wePlay: an Event used to wait for the other, or to play (set=> we play, clear=> we don't play)

	3 possibles states:
	- not in a game (_game is None)
	- his turn (_game.whoPlays == self)
	- opponent's turn (game.whoPlays != self)
	the Event _eventPlay is used for that purpuse
	"""
	allPlayers = {}

	def __init__(self, name):
		# create the logger of the player
		self._logger = logging.getLogger(name)
		# add an handler to write the log to a file (1Mo max) *if* it doesn't exist
		if not self._logger.handlers:
			file_handler = RotatingFileHandler('logs/players/'+name+'.log', 'a', 1000000, 1)
			file_handler.setLevel(logging.INFO)
			file_formatter = logging.Formatter('%(asctime)s | %(message)s', "%m/%d %H:%M:%S")
			file_handler.setFormatter(file_formatter)
			self._logger.addHandler(file_handler)


		self.logger.warning( "=================================")
		self.logger.warning( name + " just log in.")

		# name
		self._name = name

		# add itself to the dictionary of games
		self.allPlayers[name] = self

		# game
		self._game = None

		# waitGame event
		self._waitingGame = Event()
		self._waitingGame.clear()

		# weplay event
		self._wePlay = Event()
		self._wePlay.clear()


	def HTMLrepr(self):
		return "<B><A href='/player/"+self._name+"'>"+self._name+"</A></B>"


	def HTMLpage(self):
		#TODO: return a dictionary to fill a template
		return self.HTMLrepr()


	@classmethod
	def removePlayer(cls, name):
		pl = cls.getFromName(name)
		if pl is not None:
			pl.logger.warning( name +" just log out.")
			del cls.allPlayers[name]


	@classmethod
	def getFromName(cls, name):
		"""
		Get a player form its name
		:param name: (string) name of the player
		:return: the player (the object) or None if this player doesn't exist
		"""
		return cls.allPlayers.get( name, None)



	def plays(self):
		"""
		call when it's our turn (called by the opponent)
		"""
		self._wePlay.set()

	def doesnotplay(self):
		"""
		call when it's the opponent's turn
		"""
		self._wePlay.clear()


	@property
	def opponent(self):
		"""
		Return our opponent in the game
		"""
		if self._game is None
			return None
		elif self._game.player1 is self:
			return self._game.player2
		else:
			return self._game.player1



	@property
	def name(self):
		return self._name


	@property
	def logger(self):
		return self._logger

	@property
	def game(self):
		return self._game

	@game.setter
	def game(self,g):
		self._game = g
		self.logger.warning("Enter in game "+g.name)
		# since we have a game, then we can set the Event
		self._waitingGame.set()


