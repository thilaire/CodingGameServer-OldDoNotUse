"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL

File: Starships.py
	Contains the class Starships
	-> defines the Starships game (its rules, moves, etc.)

Copyright 2017 M. Pecheux
"""

from random import random, randint, choice
from re import compile
from ansi2html import Ansi2HTMLConverter
from colorama import Fore

from server.Constants import NORMAL_MOVE, WINNING_MOVE, LOSING_MOVE
from server.Game import Game
from .Constants import MOVE_UP, MOVE_DOWN, SHOOT, ASTEROID_PUSH, \
	DO_NOTHING, Ddy, INITIAL_ENERGY, SHOOT_ENERGY, ASTEROID_PUSH_ENERGY, \
	ASTEROID_POP_CHANCE

from .DoNothingPlayer import DoNothingPlayer


regdd = compile("(\d+)\s+(\d+)")  # regex to parse a "%d %d" string


def CreateBoard(sX, sY):
	"""
	Build a Board (an array of booleans: True => empty, False => asteroid)
	:param sX: order of the number of cells (over X)
	:param sY: order of the number of cells (over Y)
	Build a random (4*sX) x (2*sY+1) board containing asteroids with a given chance,
	otherwise simply an empty cell.

	Asteroids cannot pop too close to the initial positions of the players (there is
	a minimum number of columns totally empty).

	Returns a tuple (L, H, board, name).
	- L: numbers of rows
	- H: number of lines
	- board: list of lists (board[x][y] with 0 <= x <= L and 0 <= y <= H)
	- name: cutename of the Board

	"""
	L = 4*sX
	H = 2*sY+1
	# create a L*H array of True (start with empty board, then pop asteroids)
	board = [list((True,) * H) for _ in range(L)]

	# go through all cells (skip the first columns)
	for i in range(max(L//10, 10), L):
		for j in range(H):
			# get a random number and, if necessary, pop an asteroid
			if random() < ASTEROID_POP_CHANCE:
				board[i][j] = False

	# create a random 'cutename' for the Board (one that can be displayed in the server)
	nameparts1 = ['Sector', 'Galaxy', 'Quadrant', 'System', 'Planet', 'Wormhole', 'Blackhole', 'Supernova', 'Star']
	nameparts2 = ['Arcturus', 'Andromeda', 'Cassiopeia', 'of Zonn', 'of Tron', 'of Alf']
	name = choice(nameparts1) + ' '
	r = randint(0, 100)
	if r < 20:
		name += choice(['X', 'Y', 'Z', 'Theta', 'Omega', 'Alpha']) + '-' + str(randint(10, 30))
	else:
		name += choice(nameparts2)

	return L, H, board, name


class Starships(Game):
	"""
	class Starships

	Inherits from Game
	- _players: tuple of the two players
	- _logger: logger to use to log infos, debug, ...
	- _name: name of the game
	- _whoPlays: number of the player who should play now (0 or 1)
	- _waitingPlayer: Event used to wait for the players
	- _lastMove, _last_return_code: string and returning code corresponding to the last move

	Custom properties:
	- _board: array (list of lists of booleans) representing the board
	- _L, _H: length and height of the board
	- _vL: view length of the board (visible part of the board for the players)
	- _xOffset: global board x offset increasing each turn (automatic screen scrolling)
	- _playerPos: list of the coordinates of the two players (player #0 and player #1)
	- _playerEnergy: list of the energy level of the two players
	- _cutename: 'cutename' of the board (for server display of the game)
	"""

	# dictionary of the possible training Players (name-> class)
	type_dict = {"DO_NOTHING": DoNothingPlayer}


	def __init__(self, player1, player2, **options):
		"""
		Create a game
		:param player1: 1st Player
		:param player2: 2nd Player
		:param options: dictionary of options (the options 'seed' and 'timeout' are managed by the Game class)
		"""

		# random Board
		self._L, self._H, self._board, self._cutename = CreateBoard(randint(15, 20), randint(3, 5))
		self._vL = 50
		self._xOffset = 0

		# add players
		self._playerPos = []  # list of coordinates
		self._playerPos.append((0, 0))
		self._playerPos.append((0, self._H - 1))

		# level of energy
		self._playerEnergy = [INITIAL_ENERGY] * 2

		# call the superclass constructor (only at the end, because the superclass constructor launches
		# the players and they will immediately requires some Board's properties)
		super().__init__(player1, player2, **options)


	@property
	def L(self):
		"""Returns the Length of the board"""
		return self._L

	@property
	def H(self):
		"""Returns the Height of the board"""
		return self._H

	@property
	def playerPos(self):
		"""Returns the positions of the players"""
		return self._playerPos

	@property
	def playerEnergy(self):
		"""Returns the energy of the players"""
		return self._playerEnergy

	@property
	def board(self):
		"""Returns the board"""
		return self._board

	def HTMLrepr(self):
		"""Returns an HTML representation of the game"""
		return "<A href='/game/%s'>%s</A>" % (self.name, self._cutename)

	def getDictInformations(self):
		"""
		Returns a dictionary for HTML display
		:return:
		"""
		conv = Ansi2HTMLConverter()
		html = conv.convert(str(self))
		html = html.replace(u'\u2589', '<span style="background-color:black"> </span>')  # black circle
		html = html.replace(u'\u265F', 'o')  # player

		return {'boardcontent': html, 'energy': self._playerEnergy}

	def __str__(self):
		"""
		Convert a Game into string (to be send to clients, and display)
		"""
		# output storage
		lines = []

		# add game cutename (board random name)
		lines.append("\n" + self._cutename.upper() + ":")

		# add player names
		colors = [Fore.BLUE, Fore.RED]
		for i, pl in enumerate(self._players):
			br = "[]" if self._whoPlays == i else "  "
			lines.append(colors[i] + br[0] + "Player " + str(i + 1) + ": " + Fore.RESET + pl.name + colors[i] + "\t\tEnergy: " + str(self._playerEnergy[i]) + br[1] + Fore.RESET)

		# display board
		for y in range(self.H):
			st = []
			for x in range(self._xOffset, self._xOffset + self._vL):
				# add players if they are in the same place
				if (x, y) == self._playerPos[0] and (x, y) == self._playerPos[1]:
					st.append(Fore.MAGENTA + u"\u25b6" + Fore.RESET)
				# add player1
				elif (x, y) == self._playerPos[0]:
					st.append(Fore.BLUE + u"\u25b6" + Fore.RESET)
				# add player2
				elif (x, y) == self._playerPos[1]:
					st.append(Fore.RED + u"\u25b6" + Fore.RESET)
				# add empty
				elif self._board[x][y]:
					st.append(" ")
				# or add asteroid
				else:
					st.append(u"\u25cf")
			lines.append("|" + "".join(st) + "|")

		# head = "+" + "-" * (2 * self.L - 1) + "+\n"
		head = "+" + "-" * self._vL + "+\n"
		return "\n".join(lines[0:3]) + "\n" + head + "\n".join(lines[3:]) + "\n" + head

	def updateGame(self, move):
		"""
		update the game by playing a move
		- move: a string
		Return a tuple (move_code, msg), where
		- move_code: (integer) 0 if the game continues after this move, >0 if it's a winning move, -1 otherwise (illegal move)
		- msg: a message to send to the player, explaining why the game is ending
		"""

		# if won, returns the tuple (WINNING_MOVE, "congratulation message!")
		# otherwise, just returns (NORMAL_MOVE, "")

		# automatic screen scrolling
		self._xOffset += 1

		# parse the move
		result = regdd.match(move)
		# check if the data receive is valid
		if result is None:
			return LOSING_MOVE, "The move is not in correct form ('%d %d') !"
		# get the type and the value
		move_type = int(result.group(1))
		value = int(result.group(2))
		if not (MOVE_UP <= move_type <= DO_NOTHING):
			return LOSING_MOVE, "The type is not valid !"
		if move_type == SHOOT and value < 1:
			return LOSING_MOVE, "The shoot energy is not valid!"
		if move_type == ASTEROID_PUSH and not (0 <= value < self.H):
			return LOSING_MOVE, "The asteroid push line is not valid!"

		# automatic screen scrolling for all players
		for i in range(len(self._playerPos)):
			px, py = self._playerPos[i]
			# check for possible asteroid crash for other players
			if i != self._whoPlays and not self._board[px + 1][py]:
				return WINNING_MOVE, "Opponent hit asteroid!"
			self._playerPos[i] = px + 1, py

		player_x, player_y = self._playerPos[self._whoPlays]

		# move the player
		if move_type == MOVE_UP or move_type == MOVE_DOWN:
			# player move
			self._playerPos[self._whoPlays] = (player_x, player_y + Ddy[move_type])

			# check for asteroid crash
			if not self._board[player_x][player_y]:
				return LOSING_MOVE, "CRASH! You hit an asteroid!"

			# update energy
			self._playerEnergy[self._whoPlays] -= 1

			# check if player looses
			if(self._playerEnergy[self._whoPlays] <= 0):
				return LOSING_MOVE, "You are out of energy!"
			else:
				return NORMAL_MOVE, ""

		elif move_type == DO_NOTHING:
			# check for asteroid crash
			if not self._board[player_x][player_y]:
				return LOSING_MOVE, "CRASH! You hit an asteroid!"

			self._playerEnergy[self._whoPlays] -= 1

			# check if player looses
			if(self._playerEnergy[self._whoPlays] <= 0):
				return LOSING_MOVE, "You are out of energy!"
			else:
				return NORMAL_MOVE, ""

		elif move_type == SHOOT:
			# check for asteroid crash
			if not self._board[player_x][player_y]:
				return LOSING_MOVE, "CRASH! You hit an asteroid!"

			# check for energy
			if self._playerEnergy[self._whoPlays] < SHOOT_ENERGY * value:
				return LOSING_MOVE, "Not enough energy to shoot a laser Level %d!" % value

			# get line data
			shot_line = []
			for x in range(self._vL):
				shot_line.append(self._board[x][player_y])

			# move value = laser energy = nb of asteroids to destroy:
			# while laser has energy: search for the first asteroid on
			# the line, if there is one in the view window
			for i in range(1, value):
				shot_x = next((x for x in shot_line if not x), None)
				# if there is one, it is destroyed
				if shot_x is not None:
					shot_x = True

			# update energy
			self._playerEnergy[self._whoPlays] -= SHOOT_ENERGY * value

			# check if player looses
			if(self._playerEnergy[self._whoPlays] <= 0):
				return LOSING_MOVE, "You are out of energy!"
			else:
				return NORMAL_MOVE, ""

		elif move_type == ASTEROID_PUSH:
			# check for asteroid crash
			if not self._board[player_x][player_y]:
				return LOSING_MOVE, "CRASH! You hit an asteroid!"

			# check for energy
			if self._playerEnergy[self._whoPlays] < ASTEROID_PUSH_ENERGY:
				return LOSING_MOVE, "Not enough energy to pull an asteroid!"

			# move value = line of the asteroid to move // the power touches asteroids
			# on the same column as the player

			# if it is above the player, the asteroid is moved one row up
			if value < player_y:
				# if top row: if there is an asteroid, just destroy it
				if value == 0 and self._board[player_x][0] == False:
					self._board[player_x][0] = True
				# else, if there is an asteroid: move it up one row
				# if it hits another, both are destroyed
				elif value > 0 and self._board[player_x][value] == False:
					# if empty cell above, move the asteroid
					if self._board[player_x][value - 1] == True:
						self._board[player_x][value - 1] = False
					# else both asteroids cancel out: both cells are now empty
					else:
						self._board[player_x][value - 1] = True
					# anyway old spot is 'freed'
					self._board[player_x][value] = True

			# if it is beneath, it is moved one row down
			elif value > player_y:
				# if bottom row: if there is an asteroid, just destroy it
				if value == self.H - 1 and self._board[player_x][self.H - 1] == False:
					self._board[player_x][self.H - 1] = True
				# else, if there is an asteroid: move it down one row
				# if it hits another, both are destroyed
				elif value < self.H - 1 and self._board[player_x][value] == False:
					# if empty cell below, move the asteroid
					if self._board[player_x][value + 1] == True:
						self._board[player_x][value + 1] = False
					# else both asteroids cancel out: both cells are now empty
					else:
						self._board[player_x][value + 1] = True
					# anyway old spot is 'freed'
					self._board[player_x][value] = True
			# if it is the same line, it is moved to the right
			else:
				# get line data on the right of the player
				player_line = []
				for x in range(player_x + 1, self._vL):
					player_line.append(self._board[x][player_y])

				# find first asteroid
				asteroid_x = next((x for x in player_line if not x), None)
				# if last column: if there is an asteroid, just destroy it
				if asteroid_x == self._vL - 1 and self._board[self._vL - 1][player_y] == False:
					self._board[self._vL - 1][player_y] = True
				# else, if there is an asteroid: move it right one column
				# if it hits another, both are destroyed
				elif asteroid_x < self._vL - 1 and self._board[asteroid_x][player_y] == False:
					# if empty cell right to it, move the asteroid
					if self._board[asteroid_x + 1][player_y] == True:
						self._board[asteroid_x + 1][player_y] = False
					# else both asteroids cancel out: both cells are now empty
					else:
						self._board[asteroid_x + 1][player_y] = True
					# anyway old spot is 'freed'
					self._board[asteroid_x][player_y] = True

			# update energy
			self._playerEnergy[self._whoPlays] -= ASTEROID_PUSH_ENERGY

			# check if player looses
			if(self._playerEnergy[self._whoPlays] <= 0):
				return LOSING_MOVE, "You are out of energy!"
			else:
				return NORMAL_MOVE, ""

		return NORMAL_MOVE, ""

	def getDataSize(self):
		"""
		Returns the size of the next incoming data
		Here, the size of the board view window (so, not the complete length!)
		"""
		return "%d %d" % (self._vL, self.H)


	def getData(self):
		"""
		Return the data of the game (when ask with the GET_GAME_DATA message)
		Only takes into account the view window (not the entire board)
		"""
		msg = []
		for y in range(self.H):
			for x in range(self._xOffset, self._xOffset + self._vL):
				msg.append("0" if self._board[x][y] else "1")
		return "".join(msg)

	def getNextPlayer(self):
		"""
		Change the player who plays
		Returns the next player (but do not update self._whoPlays)
		"""
		return 1 - self._whoPlays       # in a tour-by-tour game, it's the opponent to play

