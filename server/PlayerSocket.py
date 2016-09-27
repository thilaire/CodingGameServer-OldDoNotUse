"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev... (not even a beta)

File: PlayerSocket.py
	Contains the Socket Handler for the player
	-> implements the protocol client <-> server
	-> answers to each request of the client

"""

import logging
from socketserver import BaseRequestHandler
from re import sub
from Player import Player

logger = logging.getLogger()  # general logger ('root')



class MyConnectionError(Exception):
	"""stupid class to manage the errors due to the connection
	"""

	# TODO: Useful ?
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)



class PlayerSocketHandler(BaseRequestHandler):
	"""
	The request handler class for our server.
	It is instantiated once per connection to the server, ie one per player
	"""

	def __init__(self, request, client_address, server):
		"""
		Call the constructor of the based class, but add an attribute
		"""
		super().__init__(request, client_address, server)
		self._player = None


	def handle(self):

		try:
			# get the name from the client and create the player
			self._player = None
			name = self.getPlayerName()
			self._player = Player(name)

			while True:
				# then, wait for a (new) game
				self.waitForGame()

				# and finally send the data for the game
				self.sendGameData()

				# repeat until we play
				while not self.game.isOver:
					data = self.receiveData()

					if data.startswith("GET_MOVE"):
						# get move of the opponent
						if self._player is not self.game.playerWhoPlays:
							self.sendData("OK")
							# get the last move
							move, return_code = self.game.getLastMove()
							# send the move and the return code
							self.sendData(move)
							self.sendData(str(return_code))
						else:
							# we cannot ask for a move, since it's our turn to play
							self.sendData("It's our turn to play, so we cannot ask for a move!")

					elif data.startswith("PLAY_MOVE "):
						# play move
						if self._player is self.game.playerWhoPlays:
							self.sendData("OK")
							# play that move to see if it's a winning/losing/normal move
							return_code, msg = self.game.receiveMove(data[10:])
							# now, send the result of the move and the associated message
							self.sendData(str(return_code))
							self.sendData(msg)
						else:
							self.sendData("It's not our turn to play, so we cannot play a move!")

					elif data.startswith("DISP_GAME"):
						# return the labyrinth
						self.sendData("OK")
						# we do not use sendData here, because we do not want to log the full message...
						self.request.sendall(str(self.game).encode())
						logger.debug("Send string to display to player %s (%s)", self._player.name, self.client_address[0])

					elif data.startswith("SEND_COMMENT "):
						# return the labyrinth
						self.sendData("OK")
						self.game.sendComment(self._player, data[13:])

					else:
						raise MyConnectionError("Bad protocol, command should not start with '" + data + "'")

				# now the game is over
				self._player.game = None    # this also kill the Game

		except MyConnectionError as e:
			# TODO: not sure if we need to stop and turnoff the connection here...
			if self._player is None:
				logger.error("Error with client (%s): '%s'", self.client_address[0], e)
			else:
				self._player.logger.error("Error with %s (%s): '%s'", self._player.name, self.client_address[0], e)



	def finish(self):
		"""
		Call when the connection is closed
		"""
		if self._player is not None:
			self._player.logger.debug("Connection closed with player %s (%s)", self._player.name, self.client_address[0])
			Player.removePlayer(self._player.name)
			del self._player

	def receiveData(self, size=1024):
		"""
		Receive data (from self.request.recv)
		and log it
		"""
		data = str(self.request.recv(size).strip(), "utf-8")
		if self._player:
			logger.debug("Receive: '%s' from %s (%s) ", data, self._player.name, self.client_address[0])
		else:
			logger.debug("Receive: '%s' from %s ", data, self.client_address[0])
		return data

	def sendData(self, data):
		"""
		Send data (with self.request.sendall) and log it
		:param data: (str) data to send
		"""
		if data:
			self.request.sendall(data.encode('utf-8'))
		else:
			# that's a trick when we want to send an empty message...
			# TODO: change this (do not send any empty message? always send X octets messages?)
			self.request.sendall('\n'.encode('utf-8'))
		if self._player:
			logger.debug("Send '%s' to %s (%s) ", data, self._player.name, self.client_address[0])
		else:
			logger.debug("Send '%s' to %s", data, self.client_address[0])


	@property
	def game(self):
		"""
		Returns the game of the player (self.game is a shortcut for self.game)
		"""
		return self._player.game





	def getPlayerName(self):
		"""
		Waits for a message "CLIENT_NAME" and treat it
		Returns the player name
		or raises an exception (MyConnectionError) if the request is not valid
		"""

		# get data
		data = self.receiveData()
		if not data.startswith("CLIENT_NAME "):
			raise MyConnectionError("Bad protocol, should start with CLIENT_NAME ")

		data = data[12:]

		# check if the player doesn't exist yet
		if data in Player.allPlayers:
			self.sendData("A client with the same name ('" + data + "') is already connected!")
			raise MyConnectionError("A client with the same name is already connected: %s (%s)" % (data, self.client_address[0]))


		# check if the name is valid (20 characters max, and only in [a-zA-Z0-9_]
		name = sub('\W+', '', data)
		if name != data or len(name) > 20:
			self.sendData("The name is invalid (max 20 characters in [a-zA-Z0-9_])")
			raise MyConnectionError("The name '%s' (from %s) is invalid (max 20 characters in [a-zA-Z0-9_])" %
			                        (data, self.client_address[0]))


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
			raise MyConnectionError("Bad protocol, should send 'WAIT_GAME' command")

		# just send back OK
		self.sendData("OK")

		# wait for the Game
		self._player.waitForGame()

		# now send the game name
		self.sendData(self.game.name)

		# now send the game sizes
		self.sendData(self.game.getDataSize())



	def sendGameData(self):
		"""
		Waits for a message "GET_GAME_DATA", and then send back the game datas
		Returns nothing
		"""

		# receive data from the socket
		data = self.receiveData()
		if not data.startswith("GET_GAME_DATA"):
			self.sendData("Bad protocol, should send 'GET_GAME_DATA' command")
			raise MyConnectionError("Bad protocol, should send 'GET_GAME_DATA' command")

		# Get the labyrinth
		self.sendData("OK")
		self.sendData(self.game.getData())
		self.sendData('0' if self.game.playerWhoPlays == self._player else '1')  # send '0' if we begin, '1' otherwise


