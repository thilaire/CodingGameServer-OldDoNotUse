#coding: utf-8
import logging
from numpy.random import seed as numpy_seed, randint, choice
from time import time
from threading import Event

# noinspection PyUnresolvedReferences
from Constants import MOVE_OK, MOVE_LOSE, MOVE_WIN, TIMEOUT_TURN


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
			raise ValueError("Players doesn't exist")
		if player1 is player2:
			raise ValueError("Cannot play against himself")
		if player1.game is not None or player2.game is not None:
			raise ValueError("Players already play in a game")

		# players
		self._players = (player1, player2)

		# get a seed if the seed is not given; seed the random numbers generator
		if seed is None:
			numpy_seed( None )	# (from doc): If seed is None, then RandomState will try to read data from /dev/urandom (or the Windows analogue) if available or seed from the clock otherwise.
			seed = randint(0, int(1e9) )
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

		self.logger.info( "=================================")
		self.logger.info( "Game %s just starts with '%s' and '%s'.", self.name, player1.name, player2.name)


		# add itself to the dictionary of games
		self.allGames[ self.name ] = self

		# advertise the players that they enter in a game
		player1.game = self
		player2.game = self

		# determine who starts
		self._whoPlays = choice( (0,1) )

		# Event to manage payMove and getMove from the players
		self._getMoveEvent = Event()
		self._getMoveEvent.clear()
		self._playMoveEvent = Event()
		self._playMoveEvent.clear()

		# last move
		self._lastMove = ""
		self._lastReturn_code = 0

		# time out for the move
		self._timeout = TIMEOUT_TURN    # maybe overloaded by a Game child class


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


	def endOfGame(self):
		"""
		Manage the end of the game
		Called when the game is over (after a move or a deconnexion)
		"""
		# log it
		self.logger.info( "The game '%s' is now finished", self.name)

		# detach the players and the game
		for p in self._players:
			p.game = None
		self._players = (None,None)



	def __del__(self):
		# remove from the dictionary of games
		#TODO: who calls this ?
		del self.allGames[self.name]


	@property
	def logger(self):
		return self._logger


	@property
	def playerWhoPlays(self ):
		"""
		Returns the player who Plays
		"""
		return self._players[ self._whoPlays ]


	def getLastMove(self):
		"""
		Wait for the move of the player playerWhoPlays
		If it doesn't answer in TIMEOUT_TURN seconds, then he losts
		Returns:
			- last move: (string) string describing the opponent last move (exactly the string it sends)
			- last return_code: (int) code (MOVE_OK, MOVE_WIN or MOVE_LOSE) describing the last move
		"""

		# wait for the move of the opponent
		self.logger.debug("Wait for playMove event")
		if self._playMoveEvent.is_set() or self._playMoveEvent.wait( self._timeout):
			self.logger.debug("Receive playMove event")
			self._playMoveEvent.clear()

			self._getMoveEvent.set()

			return self._lastMove, self._lastReturn_code
		else:
			# Timeout !!
			# the opponent has lost the game
			self._playMoveEvent.clear()

			#TODO: DO SOMETHING !!
			#TODO: signifier la fin de partie, etc.

			return self._lastMove, self._lastReturn_code


	def receiveMove(self, move):
		#TODO: changer ce nom !!! (éventuellement playMove, mais il faut renommer le playMove de labyrinth... ReceiveMove traite le move et surtout fait la synchronisation avec l'adversaire, et gère la défaite/victoire). Alors que le playMove de Labyrinth ne fait que jouer le coup et renvoyer le return_code et le message
		"""
		Play a move
		- move: a string corresponding to the move
		Return a tuple (move_code, msg), where
		- move_code: (integer) 0 if the game continues after this move, >0 if it's a winning move, -1 otherwise (illegal move)
		- msg: a message to send to the player, explaining why the game is ending"""

		# play that move
		self.logger.debug( "'%s' plays %s"%(self.playerWhoPlays.name, move))
		return_code,msg = self.playMove(move)

		# keep the last move
		self._lastMove = move
		self._lastMsg = msg
		self._lastReturn_code = return_code

		if return_code == MOVE_OK:
			# set the playMove Event
			self._playMoveEvent.set()

			# and then wait that the opponent get the move
			self.logger.debug("Wait for getMove event")
			self._getMoveEvent.wait()
			self._getMoveEvent.clear()
			self.logger.debug("Receive getMove event")

			# change who plays
			self._whoPlays = int( not self._whoPlays)

		elif return_code == MOVE_WIN:
			#TODO: signifier la fin de la partie
			#TODO: congrats, etc.
			self.endOfGame()
		else:   # return_code == MOVE_LOSE

			#TODO: signifier la fin de partie
			self.endOfGame()




		return return_code, msg



	def sendComment(self, player, comment):
		"""
			Called when a player send a comment
		Parameters:
		- player: player who sends the comment
		- comment: (string) comment
		"""
		self.logger.debug( "Player %s send this comment: '%s", player.name, comment)
		#TODO: DO SOMETHING WITH THAT COMMENT



	def playMove ( self, move ):
		"""
		Play a move
		TO BE OVERLOADED BY THE CHILD CLASS

		Play a move
		- move: a string "%d %d"
		Return a tuple (move_code, msg), where
		- move_code: (integer) 0 if the game continues after this move, >0 if it's a winning move, -1 otherwise (illegal move)
		- msg: a message to send to the player, explaining why the game is ending
		"""
		# play that move
		return True


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