"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev...

File: PlayerSocket.py
	Contains the Socket Handler for the player
	-> implements the protocol client <-> server
	-> answers to each request of the client

"""

import logging
from socketserver import BaseRequestHandler
from re import sub
from CGS.RegularPlayer import RegularPlayer
from CGS.Constants import SIZE_FMT
from CGS.Game import Game
from CGS.Constants import MOVE_LOSE, MOVE_WIN

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
			self._player = RegularPlayer(name, self.client_address[0])

			while True:
				# then, wait for a (new) game
				self.waitForGame()

				# and finally send the data for the game
				self.sendGameData()

				# repeat until we're still in the game
				while self.game is not None:
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
							# and then log the move if it's the end of the game
							if return_code == MOVE_LOSE:    # the opponent loose, so we win
								self._player.logger.info("We won the game (%s) !" % msg)
							elif return_code == MOVE_WIN:
								self._player.logger.info("We loose the game (%s) !" % msg)

						else:
							# we cannot ask for a move, since it's our turn to play
							self.sendData("It's our turn to play, so we cannot ask for a move!")
							# TODO: le player doit perdre ? ou bien on attend la déconnexion faite par l'API client ?

					elif data.startswith("PLAY_MOVE "):
						# check if it's not too late (timeout)
						if self.game is None:   # the game is already finished due to TIMEOUT
							# Timeout !
							self.sendData("OK")
							return_code, msg = MOVE_LOSE, "Timeout !"
							self.sendData(str(return_code))
							self.sendData(msg)
						# play move
						elif self._player is self.game.playerWhoPlays:
							self.sendData("OK")
							# play that move to see if it's a winning/losing/normal move
							return_code, msg = self.game.playMove(data[10:])
							# now, send the result of the move and the associated message
							self.sendData(str(return_code))
							self.sendData(msg)
						else:
							self.sendData("It's not our turn to play, so we cannot play a move!")

						# and then log the move if it's the end of the game
						if return_code == MOVE_LOSE:
							self._player.logger.info("We loose the game (%s) !" % msg)
						elif return_code == MOVE_WIN:
							self._player.logger.info("We win the game (%s) !" % msg)

					elif data.startswith("DISP_GAME"):
						# returns a (long) string describing the labyrinth
						self.sendData("OK")
						# we do not use sendData here, because we do not want to log the full message...
						head = SIZE_FMT % len(str(self.game).encode())
						self.request.sendall(str(head).encode('utf-8'))
						self.request.sendall(str(self.game).encode())
						logger.debug("Send string to display to player %s (%s)", self._player.name, self.client_address[0])

					elif data.startswith("SEND_COMMENT "):
						# receive comment
						self.sendData("OK")
						self.game.sendComment(self._player, data[13:])

					else:
						raise MyConnectionError("Bad protocol, command should not start with '" + data + "'")

		except MyConnectionError as e:
			# TODO: not sure if we need to stop and turnoff the connection here...
			# TODO: end of the game
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
			RegularPlayer.removePlayer(self._player.name)
			del self._player

	def receiveData(self, size=1024):
		"""
		Receive data (from self.request.recv)
		and log it
		"""
		data = str(self.request.recv(size).strip(), "utf-8")
		# TODO: si reçu '' alors la connection est interrompue
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
		head = SIZE_FMT % len(data.encode("utf-8"))
		self.request.sendall(str(head).encode('utf-8'))
		if data:
			self.request.sendall(data.encode('utf-8'))
		else:
			# that's a trick when we want to send an empty message...
			# TODO: change this (do not send any empty message? always send X octets messages?)
			self.request.sendall(''.encode('utf-8'))
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
		if data in RegularPlayer.allPlayers:
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
		if not data.startswith("WAIT_GAME "):
			self.sendData("Bad protocol, should send 'WAIT_GAME %d' command")
			raise MyConnectionError("Bad protocol, should send 'WAIT_GAME %d' command")

		# get the type of the game
		try:
			typeGame = int(data[10:])
		except ValueError:
			self.sendData("Bad protocol, should send 'WAIT_GAME %d' command")
			raise MyConnectionError("Bad protocol, should send 'WAIT_GAME %d' command")

		# if not a regular game
		if typeGame != 0:
			# Create a particular Game
			g = Game.getTheGameClass().gameFactory(typeGame, self._player)
			if g is None:
				self.sendData("The game type sent by '%s' command is not valid" % data)
				raise MyConnectionError("The game type sent by '%s' command is not valid" % data)

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


