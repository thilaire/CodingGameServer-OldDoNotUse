"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev... (not even a beta)

File: Player.py
	Contains the class Player
	-> defines the generic player's behavior

"""



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

		# regular
		self._isRegular = False


	def HTMLrepr(self):
		return "<B><A href='/player/"+self._name+"'>"+self._name+"</A></B>"


	def HTMLpage(self):
		# TODO: return a dictionary to fill a template
		return self.HTMLrepr()



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
	def isRegular(self):
		return self._isRegular
