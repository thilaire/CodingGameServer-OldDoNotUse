#coding: utf-8
from numpy import full
from random import shuffle,random, randint
import logging
from numpy.random import seed as numpy_seed, randint, choice
from time import time

from threading import Event



#TODO: mettre la constante quelque part (config/args?)
TIMEOUT_TURN = 10		# in seconds


def CreateLaby(sX, sY):
	"""
	Build a Labyrinth (a numpy array of booleans)
	:param sX: number of 2x2 blocks (over X)
	:param sY: number of 2x2 blocks (over Y)
	Build a random (4*sX+1) x (2*sY+1) labyrinth, symmetric with respect column 2*sX

	generation based on https://29a.ch/2009/9/7/generating-maps-mazes-with-python

	A cell is a 2x2 array
	| U X |
	| o R |
	where o is the "origin" of the cell, U and R the Up and Right "doors" (to the next cell), and X a wall (the 1st line and 2 column will be the fixed lines/columns of the labyrinth)

	The lab is composed of these cells (except that the 1st line of the lab only have the half-bottom of cells)
	and is symmetric with respect to the middle column
	
	A path is randomly generated between all these cells, and "doors" are removed accordingly

	"""
	Directions = [ (0, -1), (0, 1), (1, 0),	(-1, 0) ]

	L = 4*sX+1
	H = 2*sY+1
	lab = full( (L,H), False, dtype=bool)			# True if empty, False when we have a wall

	shuffle(Directions)
	stack = [ (0,0, list(Directions)) ] # X, Y of the cell( 2x2 cell) and directions

	while stack:
		# get the position to treat, and the possible directions
		x, y, dir = stack[-1]
		dx, dy = dir.pop()	# remove one direction

		# if it was the last direction to explore, remove that position to the stack
		if not dir:
			stack.pop()

		# new cell
		nx = x+dx
		ny = y+dy
		# check if we are out of bounds (ny==-1 is ok, but in that case, we will only consider the last line of the cell -> it will be the line number 0)
		if not (0 <= nx <= sX and -1 <= ny < sY):
			continue
		# index of the "origin" of the cell
		ox = 2*nx
		oy = 2*ny + 2
		# check if already visited
		if lab[ox,oy]:
			continue
		# else remove the corresponding wall (if within bounds)
		if ( 0 <= (ox-dx) <= (2*sX+1) ) and ( 0 <= (oy-dy) <= (2*sY+1) ):
			lab[ox-dx,oy-dy]=True
			lab[4*sX-ox+dx,oy-dy]=True	# and its symetric
		# remove the origin
		lab[ox,oy]=True
		lab[4*sX-ox,oy]=True				# and its symetric
		if random()>0.75:
			lab[ox+1,oy-1]=True
			lab[4*sX-ox-1,oy-1]=True				# and its symetric

		# add it to the stack
		shuffle(Directions)
		stack.append( ( nx, ny, list(Directions) ) )

	return lab



class Game:
	"""
	Labyrinth game
	- players: tuple of the two players
	- laby: labyrinth (numpy array for the moment)
	- logger: logger to use to log infos, debug, ...
	- name of the game
	"""

	allGames = {}

	def __init__(self, player1, player2, seed=None):
		"""
		Create a labyrinth
		:param player1: 1st Player
		:param player2: 2nd Player
		:param seed: seed of the labyrinth (same seed => same labyrinth); used as seed for the random generator
		"""
		#TODO: add size of the labyrinth ?

		# check if we can create the game (are the players available)
		if player1 is None or player2 is None:
			return None
		if player1 is player2:
			return None
		if player1.game is not None or player2.game is not None:
			return None

		# players
		self._players = (player1, player2)

		# random Labyrinth
		totalSize = randint(7,11)	# sX + sY is randomly in [7;9]
		sX = randint(3,5)
		self._lab = CreateLaby(sX,totalSize-sX)

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
		self.logger.warning( "Game %s just starts with '%s' and '%s'."% (self.name, self.player1.name, self.player2.name) )


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
	def lab(self):
		return self._lab

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


	def HTMLrepr(self):
		return "<A href='/game/%s'>%s</A>"%(self.name, self.name)

	def HTMLpage(self):
		#TODO: return a dictionary to fill a html template
		return "Game %s (with players '%s' and '%s'\n<br><br>%s"%( self.name, self.player1.name, self.player2.name, self)



	#TODO: useful ????
	@property
	def player1(self):
		return self._players[0]

	@property
	def player2(self):
		return self._players[1]

	@property
	def logger(self):
		return self._logger

	@property
	def whoPlays(self):
		return self._whoPlays


	def __str__(self):
		"""
		Convert a Game into string (to be send to clients, and display)
		"""
		#TODO: add informations about players, last move, etc.
		#TODO: add treasure and players' position
		#TODO: use unicode box-drawing characters to display the game (cf https://en.wikipedia.org/wiki/Box-drawing_character)
		#TODO: use module "colorama" to add color

		lines=[]
		L,H=self.lab.shape
		for y in range(H):
			st=""
			for x in range(L):
				st = st + (" " if self.lab[x,y] else u"\u2589")
			lines.append(st)
		return "\n".join(lines)


	@property
	def sizeX(self):
		return self.lab.shape[0]

	@property
	def sizeY(self):
		return self.lab.shape[1]



	def getLastMove(self):
		"""
		Wait for the move of the player whoPlays
		If it doesn't answer in TIMEOUT_TURN seconds, then he losts
		"""

		if self._waitingPlayer.wait( TIMEOUT_TURN ):
			self._waitingPlayer.clear()
			return self._lastMove
		else:
			# Timeout !!
			# the opponent has lost the game
			self._waitingPlayer.clear()
			#TODO: lk
			pass


	def playMove(self, move):
		"""
		Play a move
		- move: a string "%d %d"
		Return True if everything is ok, False if the move is invalid
		"""
		# play that move
		self.logger.info( "'%s' plays %s"%(self.whoPlays.name, move))
		#.....

		# and then set the Event
		self._waitingPlayer.set()
		self._whoPlays = self.whoPlays.opponent


		return True