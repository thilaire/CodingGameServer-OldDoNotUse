"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev...

File: Player.py
	Contains the class RegularPlayer
	-> defines the generic client player's behavior

"""

from threading import Event
from CGS.Logger import configurePlayerLogger
from CGS.Player import Player
from CGS.Game import Game


class RegularPlayer(Player):
	"""
	A RegularPlayer

	Inherited from Player
	- _name: its name
	- _game: the game it is involved with

	New properties/attributes
	- _logger: a logger, used to log info/debug/errors
	- _waitingGame: an Event used to wait for the game to start (set when a game is set)

	3 possibles states:
	- not in a game (_game is None)
	- his turn (_game.playerWhoPlays == self)
	- opponent's turn (game.playerWhoPlays != self)
	"""

	allPlayers = {}     # dictionary with all the regular players


	def __init__(self, name, address):
		"""
		Regular Player constructor
		Parameters:
		- name: (string) name of the player
		- address: (string) network address (used once for logging)
		"""

		# call the superclass constructor
		super().__init__(name)

		# create the logger of the player
		self._logger = configurePlayerLogger(name, Game.getTheGameName())

		self.logger.info("=================================")
		self.logger.info(name + " just log in (from " + address + ".")

		# add itself to the dictionary of (regular) players
		self.allPlayers[name] = self

		# waitGame event
		self._waitingGame = Event()
		self._waitingGame.clear()


	@property
	def isRegular(self):
		return True


	@classmethod
	def removePlayer(cls, name):
		pl = cls.getFromName(name)
		if pl is not None:
			del cls.allPlayers[name]


	@classmethod
	def getFromName(cls, name):
		"""
		Get a player form its name
		Parameters:
		- name: (string) name of the player
		Returns the player (the object) or None if this player doesn't exist
		"""
		if name in cls.allPlayers:
			return cls.allPlayers[name]
		else:
			return None
		# return cls.allPlayers.get(name, None)


	@property
	def game(self):
		return self._game

	@game.setter
	def game(self, g):
		if g is not None:
			self.logger.info("Enter in game " + g.name)
			# since we have a game, then we can set the Event
			self._waitingGame.set()
		else:
			self.logger.info("Leave the game " + self._game.name)
			# since we do not have a game, we can clear the the Event
			self._waitingGame.clear()
		self._game = g


	def waitForGame(self):
		"""
		Wait for a new game
		"""
		# WAIT until the event _waitingGame is set by the game.setter of the player
		# (so when the game assigned itself to the game property of a player)
		self._waitingGame.wait()
		self._waitingGame.clear()  # clear it for the next game...
