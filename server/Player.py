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
				data = self.receiveData()

				if data.startswith("GET_LAB:"):
					# Get the labyrinth
					self.sendData("OK")
					self.sendData("blabla")
					self.sendData( '0' if self._player.game.whoPlays == self._player else '1' )		# send '0' if we begin, '1' otherwise

				elif data.startswith("GET_MOVE:"):
					# get move of the opponent
					if self._player is not self._player.game.whoPlays:
						self.sendData("OK")
						move = self._player.game.getLastMove()
						# send that move
						#...
					else:
						# we cannot ask for a move, since it's our turn to play
						self.sendData("It's our turn to play, so we cannot ask for a move!")


				elif data.startswith("PLAY_MOVE:"):
					# play move
					if self._player is self._player.game.whoPlays:
						if self._player.game.playMove(move):
							self.sendData( "OK" )
						else:
							self.sendData( "The move is not valid!" )
					else:
						self.sendData( "It's not our turn to play, so we cannot play a move!")


				elif data.startswith("DISP_LAB:"):
					# return the labyrinth
					self.sendData( "OK")
					self.request.sendall( str(self._player.game).encode() )	# we do not use sendData here, because we do not want to log the full message...
					logger.debug("Send the labyrinth to display to player %s (%s)" % (self._player.nanme, self.client_address[0]))

				elif data.startswith("SEND_COMMENT:"):
					# return the labyrinth
					self.sendData( "OK" )
					#TODO: send a comment to the game
					#self._player.game.sendComment(data[13:])

				else:
					raise connectionError("Bad protocol, command should not start with '"+data+"'")

		except connectionError as e:
			#TODO: not sure if we need to stop and turnoff the connection here...

			if self._player:
				self._player.logger.error( "Error with %s: '%s'"%(self._player.name, self.client_address[0], e) )
			else:
				logger.error("Error with %s (%s): '%s'" % (self._player.name, self.client_address[0], e))


	def finish(self):
		"""
		Call when the connection is closed
		"""
		if self._player is not None:
			self._player.logger.debug("Connection closed with player %s (%s)"%( self._player.name, self.client_address[0]))
			Player.removePlayer(self._player.name)
			del self._player


	def receiveData(self, size=1024):
		"""
		Receive data (from self.request.recv)
		and log it
		"""
		data = str( self.request.recv(size).strip(), "utf-8" )
		if self._player:
			logger.debug( "Receive: '%s' from %s (%s) "%( data, self._player.name, self.client_address[0] ) )
		else:
			logger.debug("Receive: '%s' from %s " % (data, self.client_address[0]))
		return data


	def sendData(self, data):
		"""
		Send data (with self.request.sendall) and log it
		:param data: (str) data to send
		"""
		self.request.sendall( data.encode('utf-8') )
		if self._player:
			logger.debug( "Send '%s' to %s (%s) "%( data, self._player.name, self.client_address[0] ) )
		else:
			logger.debug("Send '%s' to %s" % (data, self.client_address[0]))


	def getPlayerName(self):
		"""
		receive and treat connection to get the player name
		:return:
		the player name
		or raises an exception (connectionError)
		"""
		data = self.receiveData()
		if not data.startswith("CLIENT_NAME: "):
			raise connectionError( "Bad protocol, should start with CLIENT_NAME: ")

		# check if the player doesn't exist yet
		if data[13:] in Player.allPlayers:
			self.sendData( "A client with the same name ('" + data[13:] + "') is already connected!" )
			raise connectionError("A client with the same name is already connected: %s (%s)"%( data[13:], self.client_address[0] ))

		# check if the name is valid (20 characters max, and only in [a-zA-Z0-9_]
		name = sub( '\W+', '',data[13:])
		if name != data[13:] or len(name)>20:
			self.sendData( "The name is invalid (max 20 characters in [a-zA-Z0-9_])" )
			raise connectionError("The name '%s' (from %s) is invalid (max 20 characters in [a-zA-Z0-9_])"%( data[13:], self.client_address[0] ))

		# just send back OK
		self.sendData("OK")
		return name


	def waitForGame(self):
		# get the WAIT_GAME message
		data = self.receiveData()
		if not data.startswith("WAIT_GAME"):
			self.sendData("Bad protocol, should send 'WAIT_GAME' command")
			raise connectionError( "Bad protocol, should send 'WAIT_GAME' command")

		# just send back OK
		self.sendData("OK")

		# wait for the Game
		self._player._waitingGame.wait()	# WAIT until the event _waitingGame is set by the game.setter of the player (so when the game assigned itself to the game property of a player)
		self._player._waitingGame.clear()	# clear it for the next game...

		# now send the game name
		self.sendData( self._player.game.name )

		# now send the game sizes
		self.sendData( "%d %d"%(self._player.game.sizeX, self._player.game.sizeY) )




class Player:
	"""
	A Player

	- _logger: a logger, used to log info/debug/errors
	- _name: its name
	- _game: the game it is involved with
	- _waitingGame: an Event used to wait for the game to start (set when a game is set)

	3 possibles states:
	- not in a game (_game is None)
	- his turn (_game.whoPlays == self)
	- opponent's turn (game.whoPlays != self)
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




	@property
	def opponent(self):
		"""
		Return our opponent in the game
		"""
		if self._game is None:
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


