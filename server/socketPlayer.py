import logging
from socketserver import ThreadingTCPServer, BaseRequestHandler
from logging.handlers import RotatingFileHandler
from re import sub
from threading import Event
from Player import Player



logger = logging.getLogger()  # general logger ('root')



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
			self._player = Player(name)

			# then, wait for a game
			self.waitForGame()

			# and finally send the data for the game
			self.sendGameData()

			while True:
				data = self.receiveData()

				if data.startswith("GET_MOVE"):
					# get move of the opponent
					if self._player is not self.game.whoPlays:
						self.sendData("OK")
						move = self.game.getLastMove()
					# send that move
					# ...
					else:
						# we cannot ask for a move, since it's our turn to play
						self.sendData("It's our turn to play, so we cannot ask for a move!")

				elif data.startswith("PLAY_MOVE "):
					# play move
					if self._player is self.game.whoPlays:
						if self.game.receiveMove(move):
							self.sendData("OK")
						else:
							self.sendData("The move is not valid!")
					else:
						self.sendData("It's not our turn to play, so we cannot play a move!")

				elif data.startswith("DISP_GAME"):
					# return the labyrinth
					self.sendData("OK")
					self.request.sendall(str(
						self.game).encode())  # we do not use sendData here, because we do not want to log the full message...
					logger.debug("Send the labyrinth to display to player %s (%s)", self._player.nanme, self.client_address[0])

				elif data.startswith("SEND_COMMENT "):
					# return the labyrinth
					self.sendData("OK")
					# TODO: send a comment to the game
					# self.game.sendComment(data[13:])

				else:
					raise connectionError("Bad protocol, command should not start with '" + data + "'")


		except connectionError as e:
			# TODO: not sure if we need to stop and turnoff the connection here...
			aLogger = self.logger if self._player is None else self._player.logger
			aLogger.error("Error with %s (%s): '%s'", self._player.name, self.client_address[0], e)



	def finish(self):
		"""
		Call when the connection is closed
		"""
		if self._player is not None:
			self._player.logger.debug( "Connection closed with player %s (%s)", self._player.name, self.client_address[0])
			Player.removePlayer(self._player.name)
			del self._player

	def receiveData(self, size=1024):
		"""
		Receive data (from self.request.recv)
		and log it
		"""
		data = str(self.request.recv(size).strip(), "utf-8")
		if self._player:
			logger.debug( "Receive: '%s' from %s (%s) ", data, self._player.name, self.client_address[0])
		else:
			logger.debug( "Receive: '%s' from %s ", data, self.client_address[0])
		return data

	def sendData(self, data):
		"""
		Send data (with self.request.sendall) and log it
		:param data: (str) data to send
		"""
		self.request.sendall( data.encode('utf-8'))
		if self._player:
			logger.debug( "Send '%s' to %s (%s) ", data, self._player.name, self.client_address[0])
		else:
			logger.debug( "Send '%s' to %s", data, self.client_address[0])


	@property
	def game(self):
		"""
		Returns the game of the player (self.game is a shortcup for self.game)
		"""
		return self._player.game





	def getPlayerName(self):
		"""
		Waits for a message "CLIENT_NAME" and treat it
		Returns the player name
		or raises an exception (connectionError) if the request is not valid
		"""

		# get data
		data = self.receiveData()
		if not data.startswith("CLIENT_NAME "):
			raise connectionError("Bad protocol, should start with CLIENT_NAME ")

		data[:13]=""

		# check if the player doesn't exist yet
		if data[13:] in Player.allPlayers:
			self.sendData("A client with the same name ('" + data[13:] + "') is already connected!")
			raise connectionError(
				"A client with the same name is already connected: %s (%s)" % (data[13:], self.client_address[0]))


		# check if the name is valid (20 characters max, and only in [a-zA-Z0-9_]
		name = sub('\W+', '', data[13:])
		if name != data[13:] or len(name) > 20:
			self.sendData("The name is invalid (max 20 characters in [a-zA-Z0-9_])")
			raise connectionError("The name '%s' (from %s) is invalid (max 20 characters in [a-zA-Z0-9_])" % (
			data[13:], self.client_address[0]))


		# just send back OK
		self.sendData("OK")
		return name



	def waitForGame(self):
		"""
		Waits for a message "WAIT_GAME" and then wait for a game (with an Event)
		Returns nothing
		"""

		# get the WAIT_GAME message
		data = self.receiveData()
		if not data.startswith("WAIT_GAME"):
			self.sendData("Bad protocol, should send 'WAIT_GAME' command")
			raise connectionError("Bad protocol, should send 'WAIT_GAME' command")

		# just send back OK
		self.sendData("OK")

		# wait for the Game
		self._player._waitingGame.wait()  # WAIT until the event _waitingGame is set by the game.setter of the player (so when the game assigned itself to the game property of a player)
		self._player._waitingGame.clear()  # clear it for the next game...

		# now send the game name
		self.sendData(self.game.name)

		# now send the game sizes
		self.sendData("%d %d" % (self.game.sizeX, self.game.sizeY))



	def sendGameData(self):
		"""
		Waits for a message "GET_GAME_DATA", and then send back the game datas
		Returns nothing
		"""

		# receive data from the socket
		data = self.receiveData()
		if not data.startswith("GET_GAME_DATA"):
			self.sendData("Bad protocol, should send 'GET_GAME_DATA' command")
			raise connectionError("Bad protocol, should send 'GET_GAME_DATA' command")

		# Get the labyrinth
		self.sendData("OK")
		self.sendData( self.game.Data() )
		self.sendData( '0' if self.game.whoPlays == self._player else '1')  # send '0' if we begin, '1' otherwise


