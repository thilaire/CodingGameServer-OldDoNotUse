"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL

File: Player.py
	Contains the class Player
	-> defines the generic player's behavior

Copyright 2016-2017 T. Hilaire, J. Brajard
"""

import logging


# disabled logger (so training players have a logger, even if it doesn't log anything)
disabledLogger = logging.getLogger("disable-logger")
disabledLogger.disabled = True



class Player:
	"""
	A Player

	- _game: the game it is involved with


	3 possibles states:
	- not in a game (_game is None)
	- his turn (_game.playerWhoPlays == self)
	- opponent's turn (game.playerWhoPlays != self)
	"""

	def __init__(self):

		# game
		self._game = None
		# the name is not stored here: for TrainingPlayer, it is stored locally, and for RegularPlayer, it is stored
		# in the BaseClas


	@property
	def game(self):
		"""Returns the game"""
		return self._game

	@game.setter
	def game(self, g):
		"""Setter of the game"""
		self._game = g

	@property
	def opponent(self):
		"""Returns the opponent of a player"""
		if self._game.players[0] is self:
			return self._game.players[1]
		else:
			return self._game.players[0]




class TrainingPlayer(Player):
	"""
		Class for training players
	"""

	def __init__(self, name):
		super().__init__()
		# name
		self._name = name
		# logger
		self._logger = disabledLogger

	@property
	def logger(self):
		"""Returns the logger"""
		return self._logger

	@property
	def name(self):
		"""Returns the name"""
		return self._name

	@property
	def isRegular(self):
		"""Indicates if the player is regular or a training player
		(it is a training player)
		"""
		return False

	def HTMLrepr(self):
		"""Returns the HTML representation of the player"""
		return "<B><A href='/player/"+self._name+"'>"+self._name+"</A></B>"

	def playMove(self):
		"""
		method that returns the move to play

		TO BE OVERLOADED BY THE CHILD CLASS

		"""
		pass
