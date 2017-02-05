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

from CGS.Player import Player
from CGS.BaseClass import BaseClass


class RegularPlayer(Player, BaseClass):
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

	allInstances = {}  # dictionary of all the instances


	def __init__(self, name, address):
		"""
		Regular Player constructor
		Parameters:
		- name: (string) name of the player
		- address: (string) network address (used once for logging)
		"""

		# call the Player constructor
		Player.__init__(self)

		# waitGame event
		self._waitingGame = Event()
		self._waitingGame.clear()

		# and last, call the BaseClass constructor
		BaseClass.__init__(self, name)
		self.logger.info("=================================")
		self.logger.info(name + " just log in (from " + address + ".")



	@property
	def isRegular(self):
		return True


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


	def HTMLrepr(self):
		return "<B><A href='/player/"+self._name+"'>"+self._name+"</A></B>"


	def HTMLpage(self):
		# TODO: return a dictionary to fill a template
		return self.HTMLrepr()
