"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev...

File: Game.py
	Contains the class Game
	-> defines the generic Game's behavior (this class will be inherits for each game, like the Labyrinth)

"""

import logging
from random import seed as set_seed, randint, choice
from time import time
from threading import Event
from os import makedirs
from datetime import datetime

from CGS.Constants import MOVE_OK, MOVE_WIN, MOVE_LOSE, TIMEOUT_TURN


class Game:
	"""
	Game class

	allGames: (class property) dictionary of all the games

	An instance of class Game contains:
	- _players: tuple of the two players (player0 and player1)
	- _logger: logger to use to log infos, debug, ...
	- _name: name of the game
	- _whoPlays: number of the player who should play now (0 or 1)
	- _waitingPlayer: Event used to wait for the player
	- _lastMove: string corresponding to the last move

	"""

	allGames = {}   #
	_theGameClass = None

	type_dict = {}          # dictionnary of the possible non-regular Players (TO BE OVERLOADED BY INHERITED CLASSES)

	def __init__(self, player1, player2, seed=None):
		"""
		Create a Game
		:param player1: 1st Player
		:param player2: 2nd Player
		:param seed: seed of the labyrinth (same seed => same labyrinth); used as seed for the random generator
		"""

		# check if we can create the game (are the players available)
		if player1 is None or player2 is None:
			raise ValueError("Players doesn't exist")
		if player1 is player2:
			raise ValueError("Cannot play against himself")
		if player1.game is not None or player2.game is not None:
			raise ValueError("Players already play in a game")

		# players
		self._players = (player1, player2)

		# get a seed if the seed is not given; seed the random numbers generator
		if seed is None:
			set_seed(None)  # (from doc):  If seed is omitted or None, current system time is used
			seed = randint(0, int(1e9))
		set_seed(seed)

		# (unique) name (unix date + seed + players name)
		self._name = str(int(time())) + '-' + str(seed) + '-' + player1.name + '-' + player2.name

		# create the logger of the game
		self._logger = logging.getLogger(self.name)
		# add an handler to write the log to a file (1Mo max) *if* it doesn't exist
		makedirs(type(self).__name__ + '/logs/games/', exist_ok=True)
		file_handler = logging.FileHandler(type(self).__name__ + '/logs/games/' + self.name + '.log')
		# file_handler.setLevel(logging.INFO)     #TODO: changer le niveau ??
		file_formatter = logging.Formatter('%(asctime)s | %(message)s', "%m/%d %H:%M:%S")
		file_handler.setFormatter(file_formatter)
		self._logger.addHandler(file_handler)

		self.logger.info("=================================")
		self.logger.info("Game %s just starts with '%s' and '%s'.", self.name, player1.name, player2.name)

		# add itself to the dictionary of games
		self.allGames[self.name] = self

		# advertise the players that they enter in a game
		player1.game = self
		player2.game = self

		# determine who starts
		self._whoPlays = choice((0, 1))

		# Event to manage payMove and getMove from the players
		self._getMoveEvent = Event()
		self._getMoveEvent.clear()
		self._playMoveEvent = Event()
		self._playMoveEvent.clear()

		# last move
		self._lastMove = ""
		self._lastReturn_code = 0

		# time out for the move
		self._timeout = TIMEOUT_TURN  # maybe overloaded by a Game child class
		self._lastMoveTime = datetime.now()     # used for the timeout when one player is a non-regular player



	@property
	def name(self):
		return self._name


	@classmethod
	def getFromName(cls, name):
		"""
		Get a game form its name (unix date + seed + players name)
		:param name: (string) name of the game
		:return: the game (the object) or None if this game doesn't exist
		"""
		if name in cls.allGames:
			return cls.allGames[name]
		else:
			return None
		# return cls.allGames.get(name, None)



	@classmethod
	def setTheGameClass(cls, theGameClass):
		"""
			Setter for the Game we are playing (in order to let that attribute be available for everyone)
			Set when the game is known and imported
		"""
		cls._theGameClass = theGameClass

	@classmethod
	def getTheGameClass(cls):
		"""
		Getter for the Game we are playing (in order to let that class be available for everyone)
		Returns the class of the game we are playing (used to create those games)
		"""
		return cls._theGameClass

	@classmethod
	def getTheGameName(cls):
		"""
		Getter for the name of the Game we are playing
		"""
		return cls._theGameClass.__name__

	def partialEndOfGame(self, whoLooses):
		"""
		manage a partial end of the game (player has deconnected or send wrong command)
		Parameters:
			- whoLooses: (RegularPlayer) player that looses
		The game is not fully ended, since we need to wait the other player to call GET_MOVE or PLAY_MOVE
		"""
		nWhoLooses = 0 if self._players[0] is whoLooses else 1
		if not self._players[1 - nWhoLooses].isRegular:
			self.endOfGame(1 - whoLooses, "Opponent has disconnected")
		else:
			self._players[nWhoLooses].game = None


	def endOfGame(self, whoWins, msg):
		"""
		Manage the end of the game:
		The game is removed from the allGames dictionary, the players do not play to that game anymore
		Is called when the game is over (after a wining/losing move)
		Parameters:
			- whoWins: (int) number of the player who wins the game
			- msg: (sting) message explaining why it's the end of the game
		"""
		# log it
		self.logger.info("%s won the game (%s) !" % (self._players[whoWins].name, msg))
		self.logger.info("The game '%s' is now finished", self.name)

		if self._players[whoWins].isRegular:
			self._players[whoWins].logger.info("We won the game (%s) !" % msg)
		if self._players[1 - whoWins].isRegular:
			self._players[1 - whoWins].logger.info("We loose the game (%s) !" % msg)

		# the players do not play anymore
		if self._players[0].game is not None:
			self._players[0].game = None
		if self._players[1].game is not None:
			self._players[1].game = None

		# remove from the list of Games
		del self.allGames[self.name]



	@property
	def logger(self):
		return self._logger


	@property
	def playerWhoPlays(self):
		"""
		Returns the player who Plays
		"""
		return self._players[self._whoPlays]




	def getLastMove(self):
		"""
		Wait for the move of the player playerWhoPlays
		If it doesn't answer in TIMEOUT_TURN seconds, then he losts
		Returns:
			- last move: (string) string describing the opponent last move (exactly the string it sends)
			- last return_code: (int) code (MOVE_OK, MOVE_WIN or MOVE_LOSE) describing the last move
		"""

		# check if the opponent doesn't have disconnected
		if self._players[self._whoPlays].game is None:
			self.endOfGame(1-self._whoPlays, "Opponent has disconnected")
			return "", MOVE_LOSE

		# wait for the move of the opponent if the opponent is a regular player
		elif self._players[self._whoPlays].isRegular:

			self.logger.debug("Wait for playMove event")
			if self._playMoveEvent.is_set() or self._playMoveEvent.wait(self._timeout):
				self.logger.debug("Receive playMove event")
				self._playMoveEvent.clear()

				self._getMoveEvent.set()

				return self._lastMove, self._lastReturn_code
			else:
				# Timeout !!
				# the opponent has lost the game
				self._playMoveEvent.clear()
				self.endOfGame(1 - self._whoPlays, "Timeout")

				return self._lastMove, MOVE_LOSE

		else:
			# otherwise, we call the opponent player's playMove method
			move = self._players[self._whoPlays].playMove()
			self.logger.debug("'%s' plays %s" % (self.playerWhoPlays.name, move))
			self._players[1 - self._whoPlays].logger.info("%s plays %s" % (self.playerWhoPlays.name, move))
			# and update the game
			return_code, msg = self.updateGame(move)

			# check if the player wins
			if return_code == MOVE_OK:
				# change who plays
				self._whoPlays = 1 - self._whoPlays

			elif return_code == MOVE_WIN:
				# Game won by the opponent, end of the game
				self.endOfGame(self._whoPlays, msg)
			else:  # return_code == MOVE_LOSE
				# Game won by the regular player, end of the game
				self.endOfGame(1 - self._whoPlays, msg)


			return move, return_code



	def playMove(self, move):
		"""
		Play a move we just received (from PlayerSocket)
		Do all the synchronization stuff (between the two players)
		The move is really played in the method updateGame (that tells if the move is legal or not)

		Parameters:
		- move: a string corresponding to the move
		Returns a tuple (move_code, msg), where
		- move_code: (integer) 0 if the game continues after this move, >0 if it's a winning move, -1 otherwise (illegal move)
		- msg: a message to send to the player, explaining why the game is ending
		"""

		# check if the opponent doesn't have disconnected
		if self._players[self._whoPlays].game is None:
			self.endOfGame(self._whoPlays, "Opponent has disconnected")
			return MOVE_WIN, "Opponent has disconnected"

		# log that move
		self.logger.debug("'%s' plays %s" % (self.playerWhoPlays.name, move))
		if self._players[self._whoPlays].isRegular:
			self._players[self._whoPlays].logger.info("I play %s" % move)
		if self._players[1 - self._whoPlays].isRegular:
			self._players[1 - self._whoPlays].logger.info("%s plays %s" % (self.playerWhoPlays.name, move))

		# check for timeout when the opponent is a non-regular player
		if not self._players[1 - self._whoPlays].isRegular:
			if (datetime.now()-self._lastMoveTime).total_seconds() > self._timeout:
				# Timeout !!
				# the player has lost the game
				self.endOfGame(1 - self._whoPlays, "Timeout")
				return MOVE_LOSE, "Timeout !"

		# play that move and update the game
		return_code, msg = self.updateGame(move)

		# keep the last move
		self._lastMove = move
		self._lastReturn_code = return_code

		# only if the opponent is a regular player
		if self._players[1 - self._whoPlays].isRegular:
			# set the playMove Event
			self._playMoveEvent.set()

			# and then wait that the opponent get the move
			self.logger.debug("Wait for getMove event")
			self._getMoveEvent.wait()
			self._getMoveEvent.clear()
			self.logger.debug("Receive getMove event")
		else:
			# if thge opponent is a non-regular player, we store the time (to compute the timeout)
			self._lastMoveTime = datetime.now()


		if return_code == MOVE_OK:
			# change who plays
			self._whoPlays = 1 - self._whoPlays
		elif return_code == MOVE_WIN:
			self.endOfGame(self._whoPlays, msg)
		else:  # return_code == MOVE_LOSE
			self.endOfGame(1 - self._whoPlays, msg)

		return return_code, msg


	def sendComment(self, player, comment):
		"""
			Called when a player send a comment
		Parameters:
		- player: player who sends the comment
		- comment: (string) comment
		"""
		self.logger.debug("Player %s send this comment: '%s", player.name, comment)

	# TODO: DO SOMETHING WITH THAT COMMENT


	@classmethod
	def gameFactory(cls, typeGame, player1):
		"""
		Create a game with a particular player
		each child class fills its own type_dict (dictionnary of the possible non-regular Players)

		1) it creates the non-regular player (according to the type)
		2) it creates the game (calling the constructor)

		Parameters:
		- typeGame: (integer) type of the game (0: regular Game, 1: play against do_nothing player, etc...)
		- player1: player who plays the game

		"""
		if typeGame in cls.type_dict:
			p = cls.type_dict[typeGame]()
			return cls(player1, p)
		else:
			return None





	def updateGame(self, move):
		"""
		update the Game by playing the move
		TO BE OVERLOADED BY THE CHILD CLASS

		Play a move and update the game
		- move: a string
		Return a tuple (move_code, msg), where
		- move_code: (integer) 0 if the game continues after this move, >0 if it's a winning move, -1 otherwise (illegal move)
		- msg: a message to send to the player, explaining why the game is ending
		"""
		# play that move
		return 0, ''


	def getData(self):
		"""
		Return the datas of the game (when ask with the GET_GAME_DATA message)

		TO BE OVERLOADED BY THE CHILD CLASS

		"""
		return ""


	def getDataSize(self):
		"""
		Returns the size of the next incoming data (for example sizes of arrays)

		TO BE OVERLOADED BY THE CHILD CLASS

		"""
		return ""





# Rajouter les méthodes HTML...
