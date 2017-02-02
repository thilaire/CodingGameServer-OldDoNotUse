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
	Contains the class Player
	-> defines the generic player's behavior

"""

import logging


# disabled logger (so training players have a logger, even if it doesn't log anything)
logger = logging.getLogger("disable-logger")
logger.disabled = True



class Player:
	"""
	A Player

	- _name: its name
	- _game: the game it is involved with


	3 possibles states:
	- not in a game (_game is None)
	- his turn (_game.playerWhoPlays == self)
	- opponent's turn (game.playerWhoPlays != self)
	"""

	def __init__(self, name):
		# name
		self._name = name

		# game
		self._game = None

		# logger
		self._logger = logger


	def HTMLrepr(self):
		return "<B><A href='/player/"+self._name+"'>"+self._name+"</A></B>"


	def HTMLpage(self):
		# TODO: return a dictionary to fill a template
		return self.HTMLrepr()


	@property
	def logger(self):
		return self._logger


	@property
	def name(self):
		return self._name



	@property
	def game(self):
		return self._game

	@game.setter
	def game(self, g):
		self._game = g


	@property
	def opponent(self):
		"""
		Returns the opponent of a player
		"""
		if self._game.players[0] is self:
			return self._game.players[1]
		else:
			return self._game.players[0]




class TrainingPlayer(Player):
	"""
		Class for training players
	"""

	@property
	def isRegular(self):
		return False


	def playMove(self):
		"""
		method that returns the move to play

		TO BE OVERLOADED BY THE CHILD CLASS

		"""
		pass
