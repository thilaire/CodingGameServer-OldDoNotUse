"""
This file is a template for a new Game in CGS

The two main methods to fill in are:
	- the __init__ to build the game (you put all the intern data here)
	- the updateMove, to check if a move is legal, to play it (and change the intern state of the game),
	and returns if the move is legal or not

Then, you should also fill:
	- the __str__ method, that build the string returns to the player to display the game
	- the getDataSize and getData methods, for the client to know the initial state of the game
	- the getDictInformations, to display the game on webpages


"""

from random import shuffle, random, randint
from ansi2html import Ansi2HTMLConverter
from colorama import Fore

from server.Constants import NORMAL_MOVE, WINNING_MOVE, LOSING_MOVE
from server.Game import Game
from .Constants import MOVE_UP, MOVE_DOWN, SHOOT, ASTEROID_PUSH, \
	DO_NOTHING, Ddy, INITIAL_ENERGY, SHOOT_ENERGY, ASTEROID_PUSH_ENERGY

# import here your training players
from .TemplateTrainingPlayer import TemplateTrainingPlayer


def CreateBoard(sX, sY):
	"""
	Build a Board (an array of booleans: True=> empty, False=> wall)
	:param sX: number of 2x2 blocks (over X)
	:param sY: number of 2x2 blocks (over Y)
	Build a random (4*sX) x (2*sY+1) board

	generation based on https://29a.ch/2009/9/7/generating-maps-mazes-with-python

	A cell is a 2x2 array
	| U X |
	| o R |
	where o is the "origin" of the cell, U and R the Up and Right "doors" (to the next cell), and X a wall
	(the 1st line and 2 column will be the fixed lines/columns of the labyrinth)

	The board is composed of these cells (except that the 1st line of the board only have the half-bottom of cells)
	and is symmetric with respect to the middle column

	A path is randomly generated between all these cells, and "doors" are removed accordingly

	Returns a tuple (L,H,board)
	- L: numbers of rows
	- H: number of lines
	- board: list of lists (board[x][y] with 0 <= x <= L and 0 <= y <= H)

	"""
	Directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]

	L = 4*sX
	H = 2*sY+1
	# create a L*H array of False
	board = [list((False,) * H) for _ in range(L)]

	shuffle(Directions)
	stack = [(0, 0, list(Directions))]  # X, Y of the cell( 2x2 cell) and directions

	while stack:
		# get the position to treat, and the possible directions
		x, y, direction = stack[-1]
		dx, dy = direction.pop()  # remove one direction

		# if it was the last direction to explore, remove that position to the stack
		if not direction:
			stack.pop()

		# new cell
		nx = x + dx
		ny = y + dy
		# check if we are out of bounds (ny==-1 is ok, but in that case, we will only consider
		# the last line of the cell -> it will be the line number 0)
		if not (0 <= nx <= sX and -1 <= ny < sY):
			continue
		# index of the "origin" of the cell
		ox = 2 * nx
		oy = 2 * ny + 2
		# check if already visited
		if board[ox][oy]:
			continue
		# else remove the corresponding wall (if within bounds)
		if (0 <= (ox - dx) <= (2 * sX + 1)) and (0 <= (oy - dy) <= (2 * sY + 1)):
			board[ox - dx][oy - dy] = True
			board[4 * sX - ox + dx][oy - dy] = True  # and its symmetric
		# remove the origin
		board[ox][oy] = True
		board[4 * sX - ox][oy] = True  # and its symmetric
		if random() > 0.75:
			board[ox + 1][oy - 1] = True
			board[4 * sX - ox - 1][oy - 1] = True  # and its symmetric

		# add it to the stack
		shuffle(Directions)
		stack.append((nx, ny, list(Directions)))

	# get random name for the Board from 2 lists
	nameparts1 = ['Sector', 'Galaxy', 'Quadrant', 'System', 'Planet', 'Wormhole', 'Blackhole', 'Supernova', 'Star']
	nameparts2 = ['Arcturus', 'Andromeda', 'Cassiopeia', 'of Zonn', 'of Tron', 'of Alf']
	name = random.choice(nameparts1) + ' '
	r = random.randint(0, 100)
	if r < 20:
		name += random.choice(['X', 'Y', 'Z', 'Theta', 'Omega', 'Alpha']) + '-' + str(random.randint(10, 30))
	else:
		name += random.choice(nameparts2)

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

	Add here your own properties
	- _board: array (list of lists of booleans) representing the board
	- _L,_H: length and height of the board
	- _vL,_vH: view length and height of the board (visible for the players)
	- _xOffset: global board x offset increasing each turn (automatic screen scrolling)
	- _playerPos: list of the coordinates of the two players (player #0 and player #1)
	- _playerEnergy: list of the energy level of the two players
	- _cutename: display 'cutename' of the board
	"""

	# dictionary of the possible training Players (name-> class)
	type_dict = {"MY_TRAINING_PLAYER": TemplateTrainingPlayer}



	def __init__(self, player1, player2, **options):
		"""
		Create a game
		:param player1: 1st Player
		:param player2: 2nd Player
		:param options: dictionary of options (the options 'seed' and 'timeout' are managed by the Game class)
		"""

		# random Board
		totalSize = randint(8, 12)  # sX + sY is randomly in [8;11]
		sX = randint(3, 5)
		self._L, self._H, self._board, self._cutename = CreateBoard(sX, totalSize - sX)
		self._vL, self._vH = 20, self._H
		self._xOffset = 0

		# add treasure and players
		self._playerPos = []  # list of coordinates
		self._playerPos.append((0, 0))
		self._playerPos.append((0, self._H - 1))

		# Level of energy
		self._playerEnergy = [INITIAL_ENERGY] * 2

		for x, y in self._playerPos:
			self._board[x][y] = True  # no wall here

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
		"""Returns an HTML representation of your game"""
		# this, or something you want...
		return "<A href='/game/%s'>%s</A>" % (self.name, self.name)

	def getDictInformations(self):
		"""
		Returns a dictionary for HTML display
		:return:
		"""
		conv = Ansi2HTMLConverter()
		html = conv.convert(str(self))
		html = html.replace(u'\u2589', '<span style="background-color:black"> </span>')  # black box
		html = html.replace(u'\u265F', 'o')  # player

		return {'boardcontent': html, 'energy': self._playerEnergy}

	def __str__(self):
		"""
		Convert a Game into string (to be send to clients, and display)
		"""
		# output storage
		lines = []

		# add game cutename (board random name)
		lines.append(self._cutename.toupper() + ":")

		# add player names
		colors = [Fore.BLUE, Fore.RED]
		for i, pl in enumerate(self._players):
			br = "[]" if self._whoPlays == i else "  "
			lines.append(br[0] + colors[i] + "Player " + str(i + 1) + ": " + Fore.RESET + pl.name + colors[i] + "(Energy: " + str(self._playerEnergy[i]) + ")" + Fore.RESET + br[1])

		# display board
		for y in range(self.H):
			st = []
			for x in range(self._xOffset, self._xOffset + self._vL):
				# add players if they are in the same place
				if (x, y) == self._playerPos[0] and (x, y) == self._playerPos[1]:
					st.append(Fore.MAGENTA + u"\u265F" + Fore.RESET)
				# add player1
				elif (x, y) == self._playerPos[0]:
					st.append(Fore.BLUE + u"\u265F" + Fore.RESET)
				# add player2
				elif (x, y) == self._playerPos[1]:
					st.append(Fore.RED + u"\u265F" + Fore.RESET)
				# add empty
				elif self.lab[x][y]:
					st.append(" ")
				# or add wall
				else:
					st.append(u"\u2589")
			# lines.append("|" + " ".join(st) + "|")
			lines.append("|" + "".join(st) + "|")

		# head = "+" + "-" * (2 * self.L - 1) + "+\n"
		head = "+" + "-" * self.L + "+\n"
		return head + "\n".join(lines) + "\n" + head

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

		# move the player
		if move_type == MOVE_UP or move_type == MOVE_DOWN:
			x, y = self._playerPos[self._whoPlays]
			x = x + 1							# automatic screen scrolling
			y = (y + Ddy[move_type])			# player movement

			if not self._board[x][y]:
				return LOSING_MOVE, "CRASH! You hit an asteroid!"

			# play the move (move the player on the lab)
			self._playerPos[self._whoPlays] = (x, y)

			# update energy
			self._playerEnergy[self._whoPlays] -= 1

			# check if player looses
			if(self._playerEnergy[self._whoPlays] <= 0):
				return LOSING_MOVE, "You are out of energy!"
			else:
				return NORMAL_MOVE, ""

		elif move_type == DO_NOTHING:
			self._playerEnergy[self._whoPlays] -= 1

			# check if player looses
			if(self._playerEnergy[self._whoPlays] <= 0):
				return LOSING_MOVE, "You are out of energy!"
			else:
				return NORMAL_MOVE, ""

		elif move_type == SHOOT:
			# check for energy
			if self._playerEnergy[self._whoPlays] < SHOOT_ENERGY * value:
				return LOSING_MOVE, "Not enough energy to shoot a laser Level %d!" % value

			# get player line
			player_y = self._playerPos[self._whoPlays][1]
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
			# check for energy
			if self._playerEnergy[self._whoPlays] < ASTEROID_PUSH_ENERGY:
				return LOSING_MOVE, "Not enough energy to pull an asteroid!"
			
			# get player line
			player_x, player_y = self._playerPos[self._whoPlays]

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
		Here, the size of the board view window
		"""
		return "%d %d" % (self._vL, self.H)


	def getData(self):
		"""
		Return the datas of the game (when ask with the GET_GAME_DATA message)
		Only takes into account the view window (not the entire board)
		"""
		msg = []
		for y in range(self.H):
			for x in range(self._xOffset, self._xOffset + self._vL):
				msg.append("0" if self.lab[x][y] else "1")
		return "".join(msg)

	def getNextPlayer(self):
		"""
		Change the player who plays
		Returns the next player (but do not update self._whoPlays)
		"""
		return 1 - self._whoPlays       # in a tour-by-tour game, it's the opponent to play

