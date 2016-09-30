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


import logging
from logging.handlers import RotatingFileHandler
from threading import Event
from os import makedirs

from CGS.Game import Game

logger = logging.getLogger()		# general logger ('root')


class Player:
	"""
	A Player

	- _logger: a logger, used to log info/debug/errors
	- _name: its name
	- _game: the game it is involved with
	- _waitingGame: an Event used to wait for the game to start (set when a game is set)

	3 possibles states:
	- not in a game (_game is None)
	- his turn (_game.playerWhoPlays == self)
	- opponent's turn (game.playerWhoPlays != self)
	"""
	allPlayers = {}     # dictionary with all the players
	gameName = ''    # name of the game, only used for the logger, initialized by runCGS

	def __init__(self, name, address):
		# create the logger of the player
		self._logger = logging.getLogger(name)
		# add an handler to write the log to a file (1Mo max) *if* it doesn't exist
		if not self._logger.handlers:
			makedirs(self.gameName + '/logs/players/', exist_ok=True)
			file_handler = RotatingFileHandler(self.gameName + '/logs/players/'+name+'.log', 'a', 1000000, 1)
			file_handler.setLevel(logging.INFO)
			file_formatter = logging.Formatter('%(asctime)s | %(message)s', "%m/%d %H:%M:%S")
			file_handler.setFormatter(file_formatter)
			self._logger.addHandler(file_handler)


		self.logger.info("=================================")
		self.logger.info(name + " just log in (from " + address + ".")

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
		# TODO: return a dictionary to fill a template
		return self.HTMLrepr()


	@classmethod
	def removePlayer(cls, name):
		pl = cls.getFromName(name)
		if pl is not None:
			pl.logger.info(name + " just log out.")
			del cls.allPlayers[name]
		# TODO: dire au jeu auquel on joue que la partie est finie ? (ou c'est déjà fait)


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
	def name(self):
		return self._name


	@property
	def logger(self):
		return self._logger


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
			Game.removeGame(self._game.name)
		self._game = g


	def waitForGame(self):
		"""
		Wait for a new game
		"""
		# WAIT until the event _waitingGame is set by the game.setter of the player
		# (so when the game assigned itself to the game property of a player)
		self._waitingGame.wait()
		self._waitingGame.clear()  # clear it for the next game...
