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
from datetime import datetime

from CGS.Constants import MOVE_OK, MOVE_WIN, MOVE_LOSE, TIMEOUT_TURN, MAX_COMMENTS
from CGS.Logger import configureGameLogger
from CGS.Comments import CommentQueue
from geventwebsocket import WebSocketError


def crc24(octets):
	"""
	Compute a CRC 24 bits hash
	Credits Karl Knechtel
	http://stackoverflow.com/questions/4544154/crc24-from-c-to-python
	"""
	INIT = 0xB704CE
	POLY = 0x1864CFB
	crc = INIT
	for octet in octets:
		crc ^= (octet << 16)
		for i in range(8):
			crc <<= 1
			if crc & 0x1000000:
				crc ^= POLY
	return crc & 0xFFFFFF


def hex6(x):
	"""
	Returns (a string) the hexadecimal of x (but with 6 digits, without the trailing 0x)
	"""
	h = "000000" + hex(x)[2:]       # add zeros before the hexadecimal (without 0x)
	return h[-6:]   # get the 6 last characters


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
	- _tournament: (Tournament) the tournament the game is involved in (or None no tournament)

	"""

	allGames = {}   # TODO: private member ? (idem for all other classes with ther allXxxxx)
	_theGameClass = None

	type_dict = {}          # dictionary of the possible training Players (TO BE OVERLOADED BY INHERITED CLASSES)

	def __init__(self, player1, player2, tournament=None, **options):
		"""
		Create a Game
		Parameters:
		- player1, player2: two Player (the order will be changed according who begins)
		- options: dictionary of options
			- 'seed': seed of the labyrinth (same seed => same labyrinth); used as seed for the random generator
			- 'timeout': timeout of the game (if not given, the default timeout is used)
			- 'start': who starts the game (0 or 1); random when not precised
			# TODO: add a delay/pause option (in second)
		"""

		# check if we can create the game (are the players available)
		if player1 is None or player2 is None:
			raise ValueError("Players doesn't exist")
		if player1 is player2:
			raise ValueError("Cannot play against himself")
		if player1.game is not None or player2.game is not None:
			raise ValueError("Players already play in a game")

		# players
		# we randomly decide the order of the players
		if 'start' not in options:
			pl = choice((0, 1))
		else:
			try:
				pl = int(options['start'])
			except ValueError:
				raise ValueError("The 'start' option must be '0' or '1'")
		self._players = (player1, player2) if pl == 0 else (player2, player1)



		# get a seed if the seed is not given; seed the random numbers generator
		if 'seed' not in options:
			set_seed(None)  # (from doc):  If seed is omitted or None, current system time is used
			seed = randint(0, 16777215)     # between 0 and 2^24-1
		else:
			try:
				seed = int(options['seed'])
				if not 0 <= seed <= 16777215:
					raise ValueError("The 'seed' value must be between 0 and 16777215 ('seed=%s'." % options['seed'])
			except ValueError:
				raise ValueError("The 'seed' value is invalid ('seed=%s')" % options['seed'])
		set_seed(seed)


		# (unique) name composed by
		# - the first 6 characters are the seed (in hexadecimal),
		# - the 6 next characters are hash (CRC24) of the time and names (hexadecimal)
		ok = False
		while not ok:   # we need a loop just in case we are unlucky and two existing games have the same hash
			name = str(int(time())) + player1.name + player2.name
			self._name = hex6(seed)[2:] + hex6(crc24(bytes(name, 'utf8')))[2:]
			ok = self._name not in self.allGames
			if not ok:
				# just in case we are unlucky, we need to log it (probably it will never happens)
				logger = logging.getLogger()
				og = self.allGames[self._name]  # other game
				g1 = str(og.seed) + '-' + og.players[0].name + og.players[1].name
				g2 = str(seed) + '-' + player1.name + '-' + player2.name
				logger.warning("Two games have the same name (same hash): %s and %s" % (g1, g2))

		# store the tournament
		self._tournament = tournament

		# create the logger of the game
		self._logger = configureGameLogger(self.name)
		# log the game
		self.logger.info("=================================")
		self.logger.message("Game %s just starts with '%s' and '%s' (seed=%d).", self.name, player1.name, player2.name, seed)
		# TODO: logguer qu'il s'agit d'un tournoi si tournament is not None

		# determine who starts (player #0 ALWAYS starts)
		self._whoPlays = 0

		# Event to manage payMove and getMove from the players
		self._getMoveEvent = Event()
		self._getMoveEvent.clear()
		self._playMoveEvent = Event()
		self._playMoveEvent.clear()

		# last move
		self._lastMove = ""
		self._lastReturn_code = 0

		# time out for the move
		if 'timeout' not in options:
			self._timeout = TIMEOUT_TURN
		else:
			try:
				self._timeout = int(options['timeout'])
			except ValueError:
				raise ValueError("The 'timeout' value is invalid ('timeout=%s')" % options['timeout'])

		# timestamp of the last move
		self._lastMoveTime = datetime.now()     # used for the timeout when one player is a non-regular player

		# list of comments
		self._comments = CommentQueue(MAX_COMMENTS)

		# advertise the players that they enter in a game
		player1.game = self
		player2.game = self

		# List of websockets to send the game data
		self.lwsock = []
		# and last, add itself to the dictionary of games
		self.allGames[self.name] = self




	@property
	def name(self):
		return self._name

	def HTMLpage(self):
		return ''

	def addsock(self, wsock):
		self.lwsock.append(wsock)

	def send_wsock(self):
		if self.lwsock:
			for wsock in self.lwsock:
				try:
					print("sending message to wsock")
					wsock.send(self.HTMLdict()['HtmlPage'])
				except WebSocketError:
					pass

	def HTMLdict(self):
		d = dict()
		d['GameName'] = self.name
		d['Player1'] = self.players[0].name
		d['Player2'] = self.players[1].name
		d['HtmlPage'] = self.HTMLpage()
		return d

	def HTMLrepr(self):
		return "<B><A href='/game/%s'>%s</A></B> (%s vs %s)" % \
		       (self.name, self.name, self.players[0].name, self.players[1].name)


	def partialEndOfGame(self, whoLooses):
		"""
		manage a partial end of the game (player has deconnected or send wrong command)
		Parameters:
			- whoLooses: (RegularPlayer) player that looses
		The game is not fully ended, since we need to wait the other player to call GET_MOVE or PLAY_MOVE
		"""
		nWhoLooses = 0 if self._players[0] is whoLooses else 1
		if not self._players[1 - nWhoLooses].isRegular:
			self.endOfGame(1 - nWhoLooses, "Opponent has disconnected")
		else:
			whoLooses.game = None
			self.logger.debug("1) Player %s's game set to None" % whoLooses.name)


	def manageNextTurn(self, return_code, msg):
		"""
		Called after having update the game
		Check if it's the end of the game (and call endOfGame), or update the next player
		Parameters:
		- return_code: (int) code returned by updateGame (MOVE_OK, MOVE_WIN or MOVE_LOSE)
		- msg: (string) message when the move is not OK
		"""
		# check if the player wins
		if return_code == MOVE_OK:
			# change who plays
			self._whoPlays = self.getNextPlayer()
		elif return_code == MOVE_WIN:
			# Game won by the opponent, end of the game
			self.endOfGame(self._whoPlays, msg)
		else:  # return_code == MOVE_LOSE
			# Game won by the regular player, end of the game
			self.endOfGame(1 - self._whoPlays, msg)


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
		self.logger.message("The game '%s' is now finished, %s won against %s (%s)",
		                    self.name, self._players[whoWins].name, self._players[1-whoWins].name, msg)
		self._players[whoWins].logger.info("We won the game (%s) !" % msg)
		self._players[1 - whoWins].logger.info("We loose the game (%s) !" % msg)

		# the players do not play anymore
		if self._players[0].game is not None:
			self._players[0].game = None
			self.logger.debug("2) Player %s's game set to None" % self._players[0].name)    # TODO: to remove
		if self._players[1].game is not None:
			self._players[1].game = None
			self.logger.debug("3) Player %s's game set to None" % self._players[1].name)    # TODO: to remove

		# tell the tournament the result of the game
		if self._tournament:
			self._tournament.endOfGame(self._players[whoWins], self._players[1 - whoWins])

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


	@property
	def players(self):
		"""
		Returns the players
		"""
		return self._players


	def getLastMove(self):
		"""
		Wait for the move of the player playerWhoPlays (and sync with it)
		If it doesn't answer in TIMEOUT_TURN seconds, then he losts the game
		Returns:
			- last move: (string) string describing the opponent last move (exactly the string it sends)
			- last return_code: (int) code (MOVE_OK, MOVE_WIN or MOVE_LOSE) describing the last move
		"""

		# check if the opponent doesn't have disconnected
		if self._players[self._whoPlays].game is None:
			self.endOfGame(1-self._whoPlays, "Opponent has disconnected")
			return "", MOVE_LOSE

		# wait for the move of the opponent if the opponent is a regular player
		if self._players[self._whoPlays].isRegular:
			toto= "getMove ("+self._players[1-self._whoPlays].name+")"
			# 1st synchronization with the opponent (with playMove)
			self.logger.low_debug("1st synchronization with opponent (getMove)")
			if syncEvents(self.logger, toto, self._getMoveEvent, self._playMoveEvent, self._timeout):
				# now the opponent has played, we wait now for self._whoPlays to be updated
				self.logger.low_debug("2nd synchronization with opponent (getMove)")
				syncEvents(self.logger, toto, self._getMoveEvent, self._playMoveEvent)
				return self._lastMove, self._lastReturn_code
			else:
				# Timeout !!
				# the opponent has lost the game
				self.endOfGame(1 - self._whoPlays, "Timeout")
				return self._lastMove, MOVE_LOSE

		else:
			# the opponent is a training player
			# so we call its playMove method
			move = self._players[self._whoPlays].playMove()
			self.logger.info("'%s' plays %s" % (self._players[self._whoPlays].name, move))
			self._players[1 - self._whoPlays].logger.info("%s plays %s" % (self._players[self._whoPlays].name, move))

			# and update the game
			return_code, msg = self.updateGame(move)

			# update who plays next and check for the end of the game
			self.manageNextTurn(return_code, msg)

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
		self.logger.info("'%s' plays %s" % (self.players[self._whoPlays].name, move))
		if self._players[self._whoPlays].isRegular:
			self._players[self._whoPlays].logger.info("I play %s" % move)
		if self._players[1 - self._whoPlays].isRegular:
			self._players[1 - self._whoPlays].logger.info("%s plays %s" % (self.players[self._whoPlays].name, move))


		# if the opponent is a regular player
		if self._players[1 - self._whoPlays].isRegular:
			toto = "playMove ("+self._players[self._whoPlays].name+")"
			# play that move, update the game and keep the last move
			return_code, msg = self.updateGame(move)
			self._lastMove = move
			self._lastReturn_code = return_code

			# 1st synchronization with the opponent
			self.logger.low_debug("1st synchronization with opponent (playMove)")
			if not syncEvents(self.logger, toto, self._playMoveEvent, self._getMoveEvent, self._timeout):
				self.endOfGame(self._whoPlays, "Timeout")
				return MOVE_WIN, "Timeout of the opponent!"

			# update who plays next and check for the end of the game
			self.manageNextTurn(return_code, msg)

			# 2nd synchronization with the opponent
			self.logger.low_debug("2nd synchronization with opponent (playMove)")
			syncEvents(self.logger, toto, self._playMoveEvent, self._getMoveEvent)


		else:   # when the opponent is a training player
			# check for timeout
			if (datetime.now()-self._lastMoveTime).total_seconds() > self._timeout:
				# Timeout !!
				# the player has lost the game
				self.endOfGame(1 - self._whoPlays, "Timeout")
				return MOVE_LOSE, "Timeout !"

			# play that move, update the game and keep the last move
			return_code, msg = self.updateGame(move)
			self._lastMove = move
			self._lastReturn_code = return_code

			# update who plays next and check for the end of the game
			self.manageNextTurn(return_code, msg)

			#  we store the time (to compute the timeout)
			self._lastMoveTime = datetime.now()

		self.send_wsock()
		return return_code, msg


	def sendComment(self, player, comment):
		"""
			Called when a player send a comment
		Parameters:
		- player: player who sends the comment
		- comment: (string) comment
		"""
		# log it
		self.logger.info("[%s] : '%s'", player.name, comment)
		for n in (0, 1):
			self.players[n].logger.info("[%s] : %s" % (player.name, comment))

		# append comment
		nPlayer = 0 if player is self._players[0] else 1
		self._comments.append(comment, nPlayer)




	def display(self, player):
		"""
		Parameters:
			- player: player who ask for display

		Returns a string version of the game, composed of:
		- the game information (from __str__ of the inherited class)
		- the comments
		"""
		nPlayer = 0 if player is self._players[0] else 1
		return str(self) + "\n" + self._comments.getString(nPlayer, [p.name for p in self._players]) + "\n"*4



	@classmethod
	def gameFactory(cls, name, player1, options):
		"""
		Create a game with a particular player
		each child class fills its own type_dict (dictionary of the possible non-regular Players)

		1) it creates the training player (according to the type name)
		2) it creates the game (calling the constructor)

		Parameters:
		- name: (string) type of the training player ("DO_NOTHING": play against do_nothing player, etc...)
		- player1: player who plays the game
		- options: (dict) some options given by the player

		"""
		if name in cls.type_dict:
			p = cls.type_dict[name](**options)    # may raise ValueError exception if the options are invalid
			return cls(player1, p, **options)     # may raise ValueError exception if the options are invalid
		else:
			raise ValueError("The training player name '%s' is not valid." % name)


	@classmethod
	def getFromName(cls, name):
		"""
		Get a game form its name (seed + hash of time + players name)
		Parameters:
		- name: (string) name of the game

		Returns the game (the object) or None if this game doesn't exist
		"""
		return cls.allGames.get(name, None)


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


	def getNextPlayer(self):
		"""
		Change the player who plays

		IT CAN BE OVERLOADED BY THE CHILD CLASS if the behaviour is different than a tour by tour game
		(if a player can replay)

		Returns the next player (but do not update self._whoPlays)
		"""
		return 1 - self._whoPlays


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




def syncEvents(logger, name, myEvent, otherEvent, timeout=None):
	"""
	Synchronize two threads using two Events

	Parameters:
	- myEvent: (Event) my Event for the synchronization
	- otherEvent: (Event) the Event of the other thread
	- timeout: (None or int) time (in seconds) before timeout

	Returns False if the timeout occurs, else True
	"""
	# set my Event
	logger.low_debug(name+": myEvent.set()")
	myEvent.set()
	# wait for the other Event
	logger.low_debug(name+": otherEvent.wait")
	ret = otherEvent.is_set() or otherEvent.wait(timeout)       # TODO: is is_set necessary ?
	# receive other Event
	logger.low_debug(name+": otherEvent.clear()")
	otherEvent.clear()
	return ret
