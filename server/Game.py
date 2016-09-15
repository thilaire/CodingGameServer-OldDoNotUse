#coding: utf-8
import logging
from numpy.random import seed as numpy_seed, randint, choice
from time import time
from threading import Event


#TODO: mettre la constante quelque part (config/args?)
TIMEOUT_TURN = 10		# in seconds


class Game:
	"""
	Game class

	allGames: (class property) dictionary of all the games

	An instance of class Game contains:
	- _players: tuple of the two players
	- _logger: logger to use to log infos, debug, ...
	- _name: name of the game
	- _whoPlays: player who should play now
	- _waitingPlayer: Event used to wait for the player
	- _lastMove: string corresponding to the last move

	"""

	allGames = {}

	def __init__(self, player1, player2, seed=None):
		"""
		Create a Game
		:param player1: 1st Player
		:param player2: 2nd Player
		:param seed: seed of the labyrinth (same seed => same labyrinth); used as seed for the random generator
		"""

		# check if we can create the game (are the players available)
		if player1 is None or player2 is None:
			return None
		if player1 is player2:
			return None
		if player1.game is not None or player2.game is not None:
			return None

		# players
		self._players = (player1, player2)

		# get a seed if the seed is not given; seed the random numbers generator
		if seed is None:
			numpy_seed( None )	# (from doc): If seed is None, then RandomState will try to read data from /dev/urandom (or the Windows analogue) if available or seed from the clock otherwise.
			seed = randint(0, 1e9)
		numpy_seed(seed)

		# (unique) name (unix date + seed + players name)
		self._name = str( int(time())) + '-' + str(seed) + '-' + player1.name + '-' + player2.name

		# create the logger of the game
		self._logger = logging.getLogger(self.name)
		# add an handler to write the log to a file (1Mo max) *if* it doesn't exist
		file_handler = logging.FileHandler('logs/games/'+self.name+'.log')
		file_handler.setLevel(logging.INFO)
		file_formatter = logging.Formatter('%(asctime)s | %(message)s', "%m/%d %H:%M:%S")
		file_handler.setFormatter(file_formatter)
		self._logger.addHandler(file_handler)

		self.logger.warning( "=================================")
		self.logger.warning( "Game %s just starts with '%s' and '%s'."% (self.name, player1.name, player2.name) )


		# add itself to the dictionary of games
		self.allGames[ self.name ] = self

		# advertise the players that they enter in a game
		player1.game = self
		player2.game = self

		# determine who starts
		self._whoPlays = choice( (player1, player2) )
		self._waitingPlayer = Event()
		self._waitingPlayer.clear()		# we're waiting for whoPlays to play its move


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
		return cls.allGames.get( name, None)


	def __del__(self):

		self.logger.info( "The game '%s' is now finished", self.name)
		del self.allGames[ self.name ]


	@property
	def logger(self):
		return self._logger


	@property
	def whoPlays(self):
		return self._whoPlays


	def getLastMove(self):
		"""
		Wait for the move of the player whoPlays
		If it doesn't answer in TIMEOUT_TURN seconds, then he losts
		"""

		if self._waitingPlayer.is_set() or self._waitingPlayer.wait( TIMEOUT_TURN ):
			self._waitingPlayer.clear()
			return self._lastMove
		else:
			# Timeout !!
			# the opponent has lost the game
			self._waitingPlayer.clear()
			#TODO: lk
			pass


	def receiveMove(self, move):
		"""
		Play a move
		- move: a string corresponding to the move
		Return True if everything is ok, False if the move is invalid
		"""
		# play that move
		self.logger.info( "'%s' plays %s"%(self.whoPlays.name, move))
		#TODO:
		valid = self.playMove(self, move)

		if valid:

			# keep the last move
			self._lastMove = move

			# and then set the Event
			self._waitingPlayer.set()
			self._whoPlays = self.whoPlays.opponent

			return True


		else:
			#TODO: something to do, here?
			return False