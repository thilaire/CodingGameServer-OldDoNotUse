# coding: utf-8
from numpy import full
from random import shuffle, random, randint
from numpy.random import randint
from Game import Game
from colorama import Fore


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
	Directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]

	L = 4 * sX + 1
	H = 2 * sY + 1
	lab = full((L, H), False, dtype=bool)  # True if empty, False when we have a wall

	shuffle(Directions)
	stack = [(0, 0, list(Directions))]  # X, Y of the cell( 2x2 cell) and directions

	while stack:
		# get the position to treat, and the possible directions
		x, y, dir = stack[-1]
		dx, dy = dir.pop()  # remove one direction

		# if it was the last direction to explore, remove that position to the stack
		if not dir:
			stack.pop()

		# new cell
		nx = x + dx
		ny = y + dy
		# check if we are out of bounds (ny==-1 is ok, but in that case, we will only consider the last line of the cell -> it will be the line number 0)
		if not (0 <= nx <= sX and -1 <= ny < sY):
			continue
		# index of the "origin" of the cell
		ox = 2 * nx
		oy = 2 * ny + 2
		# check if already visited
		if lab[ox, oy]:
			continue
		# else remove the corresponding wall (if within bounds)
		if (0 <= (ox - dx) <= (2 * sX + 1)) and (0 <= (oy - dy) <= (2 * sY + 1)):
			lab[ox - dx, oy - dy] = True
			lab[4 * sX - ox + dx, oy - dy] = True  # and its symetric
		# remove the origin
		lab[ox, oy] = True
		lab[4 * sX - ox, oy] = True  # and its symetric
		if random() > 0.75:
			lab[ox + 1, oy - 1] = True
			lab[4 * sX - ox - 1, oy - 1] = True  # and its symetric

		# add it to the stack
		shuffle(Directions)
		stack.append((nx, ny, list(Directions)))

	return lab


class Labyrinth(Game):
	"""
	Labyrinth game
	Inherits from Game
	- _players: tuple of the two players
	- _logger: logger to use to log infos, debug, ...
	- _name: name of the game
	- _whoPlays: player who should play now
	- _waitingPlayer: Event used to wait for the player
	- _lastMove: string corresponding to the last move

	Add some properties
	- lab: numpy array representing the labyrinth


	"""

	allGames = {}

	def __init__(self, player1, player2, seed=None):
		"""
		Create a labyrinth
		:param player1: 1st Player
		:param player2: 2nd Player
		:param seed: seed of the labyrinth (same seed => same labyrinth); used as seed for the random generator
		"""

		# call the superclass constructor
		super(Labyrinth, self).__init__(player1, player2)

		# TODO: add size of the labyrinth ?

		# random Labyrinth
		totalSize = randint(7, 11)  # sX + sY is randomly in [7;9]
		sX = randint(3, 5)
		self._lab = CreateLaby(sX, totalSize - sX)

		# add treasor and players
		L,H = self.lab.shape
		self._treasure = (L // 2, H // 2)
		self._lab[ self._treasure] = False

		self._player1 = (0, H // 2)
		self._lab[ self._player1] = False

		self._player2 = (L - 1, H // 2)
		self._lab[ self._player2] = False




	@property
	def lab(self):
		return self._lab


	def HTMLrepr(self):
		return "<A href='/game/%s'>%s</A>" % (self.name, self.name)

	def HTMLpage(self):
		# TODO: return a dictionary to fill a html template
		return "Game %s (with players '%s' and '%s'\n<br><br>%s" % (self.name, self._player1.name, self._player2.name, self)



	def __str__(self):
		"""
		Convert a Game into string (to be send to clients, and display)
		"""
		# TODO: add informations about players, last move, etc.
		# TODO: add treasure and players' position
		# TODO: use unicode box-drawing characters to display the game (cf https://en.wikipedia.org/wiki/Box-drawing_character)
		# TODO: use module "colorama" to add color

		lines = []
		L, H = self.lab.shape
		for y in range(H):
			st = []
			for x in range(L):
				# add treasor
				if (x,y) == self._treasure:
					st.append( Fore.GREEN + u"\u2691" + Fore.RESET)
				# add player1
				elif (x,y) == self._player1:
					st.append( Fore.BLUE + u"\u265F" + Fore.RESET)
				# add player2
				elif (x,y) == self._player2:
					st.append( Fore.RED + u"\u265F" + Fore.RESET)
				# add empty
				elif self.lab[x,y]:
					st.append( " ")
				# or add wall
				else:
					st.append( u"\u2589")
			lines.append( "|" + " ".join(st) + "|" )

		# add player names
		#TODO: add points
		brackets0 = "[]" if self._whoPlays==self._players[0] else "  "
		brackets1 = "[]" if self._whoPlays == self._players[1] else "  "
		lines[H//2] = lines[H//2] + "\t\t" + brackets0[0] + Fore.BLUE + "Player 1: " + Fore.RESET + self._players[0].name + brackets0[1]
		lines[H//2 + 2] = lines[H//2 + 2] + "\t\t" + brackets1[0] + Fore.RED + "Player 2: " + Fore.RESET + self._players[1].name + brackets1[1]

		head = "+"+"-"*(2*L-1)+"+\n"
		return head + "\n".join(lines) + "\n" + head


	@property
	def sizeX(self):
		return self.lab.shape[0]


	@property
	def sizeY(self):
		return self.lab.shape[1]


	def playMove(self, move):
		"""
		Play a move
		- move: a string "%d %d"
		Return True if everything is ok, False if the move is invalid
		"""
		# play that move

		return True

	def getData(self):
		"""
		Return the datas of the labyrinth (when ask with the GET_GAME_DATA message)
		"""
		msg = []
		L, H = self.lab.shape
		for y in range(H):
			for x in range(L):
				msg.append( "1" if self.lab[x, y] else "0")
		return "".join(msg)