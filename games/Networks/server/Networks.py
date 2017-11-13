"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL

File: Network.py
	Contains the class Networks
	-> defines the Networks game (its rules, moves, etc.)

Copyright 2017 M. Pecheux
"""

from random import random, randint, choice, shuffle
from re import compile
from ansi2html import Ansi2HTMLConverter
from colorama import Fore

from server.Constants import NORMAL_MOVE, WINNING_MOVE, LOSING_MOVE
from server.Game import Game
from .Constants import CAPTURE, DESTROY, LINK_H, LINK_V, DO_NOTHING, \
	LINK_ENERGY, DESTROY_ENERGY, NODE_CODES_START_ID, NODE_DISPLAY_CODES, \
	NODE_TYPES, NODE_CODES_LENGTH, MAX_NODES_COUNT

from .DoNothingPlayer import DoNothingPlayer
from .AliceRandomPlayer import AliceRandomPlayer
from .WhiteRabbitPlayer import WhiteRabbitPlayer
from .NeoPlayer import NeoPlayer


regdd = compile("(\d+)\s+(\d+)\s+(\d+)")  # regex to parse a "%d %d" string


class Node:
	def __init__(self, x, y, ntype, isGoal):
		self.x = x
		self.y = y
		self.owner = -1
		self.type = ntype
		self.isGoal = isGoal
		self.state = 0
		self.delay = -1

	def set_capture(self, player, incapture_nodes):
		self.owner = player
		self.delay = len(NODE_DISPLAY_CODES[self.type]) - 1
		incapture_nodes.append(self)

	def check_capture(self, player_nodes, incapture_nodes):
#		print('(%d,%d) - delay = %d, state = %d' % (self.x, self.y, self.delay, self.state))
		if self.delay == 0:
			self.capture(self.owner)
			player_nodes.append(self)
			incapture_nodes.remove(self)
			return True
		elif self.delay > 0:
			self.state += 1
			self.delay -= 1
			return False

	def capture(self, player):
		self.owner = player
		self.state = len(NODE_DISPLAY_CODES[self.type]) - 1
		self.delay = -1

	def display_str(self):
		if self.isGoal and self.delay == -1:
			return Fore.GREEN + NODE_DISPLAY_CODES[self.type][len(NODE_DISPLAY_CODES[self.type]) - 1] + Fore.RESET
		if self.owner == -1:
			return NODE_DISPLAY_CODES[self.type][self.state]
		elif self.owner == 0:
			return Fore.BLUE + NODE_DISPLAY_CODES[self.type][self.state] + Fore.RESET
		elif self.owner == 1:
			return Fore.RED + NODE_DISPLAY_CODES[self.type][self.state] + Fore.RESET

	def display_html(self):
		if self.isGoal and self.delay == -1:
			return '<span style="color: var(--green-color);">' + NODE_DISPLAY_CODES[self.type][len(NODE_DISPLAY_CODES[self.type]) - 1] + '</span>'
		if self.owner == -1:
			return '<span>' + NODE_DISPLAY_CODES[self.type][self.state] + '</span>'
		elif self.owner == 0:
			return '<span style="color: var(--blue-color);">' + NODE_DISPLAY_CODES[self.type][self.state] + '</span>'
		elif self.owner == 1:
			return '<span style="color: var(--red-color);">' + NODE_DISPLAY_CODES[self.type][self.state] + '</span>'

	def __str__(self):
		return str(NODE_CODES_START_ID + (self.owner+1)*NODE_CODES_LENGTH + sum(map(len, NODE_DISPLAY_CODES[:self.type])) + self.state)


class Link:
	def __init__(self, direction):
		self.direction = direction

	def display_str(self):
		if self.direction == 0:
			return "-"
		elif self.direction == 1:
			return "|"

	def display_html(self):
		if self.direction == 0:
			return u"\u2014"
		elif self.direction == 1:
			return "|"

	def __str__(self):
		return str(self.direction + 1)


def CreateBoard(sX, sY):
	"""
	Build a Board (an array of elements = Node, Link or None)
	:param sX: number of 2x2 blocks (over X)
	:param sY: number of 2x2 blocks (over Y)
	Build a random (4*sX+1) x (2*sY+1) board, symmetric with respect middle point

	generation based on https://29a.ch/2009/9/7/generating-maps-mazes-with-python

	A cell is a 2x2 array
	| U X |
	| o R |
	where o is the "origin" of the cell, U and R the Up and Right "doors" (to the next cell), and X a wall
	(the 1st line and 2 column will be the fixed lines/columns of the board)

	The board is composed of these cells (except that the 1st line of the board only have the half-bottom of cells)
	and is symmetric with respect to the middle point

	A path is randomly generated between all these cells, and "doors" are removed accordingly

	Returns a tuple (L,H,board)
	- L: numbers of rows
	- H: number of lines
	- board: list of lists (board[x][y] with 0 <= x <= L and 0 <= y <= H)

	"""
	Directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]

	L = 4 * sX + 1
	H = 2 * sY + 1
	# create a L*H array of None
	board = [list((None,) * H) for _ in range(L)]

	shuffle(Directions)
	stack = [(0, 0, list(Directions))]  # X, Y of the cell( 2x2 cell) and directions
	current_node_counts = [0] * len(MAX_NODES_COUNT)

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
			if dx == 0:
				board[ox - dx][oy - dy] = Link(1)
			else:
				board[ox - dx][oy - dy] = Link(0)
		# remove the origin and choose random type
		available_node_types = []
		for i in range(len(MAX_NODES_COUNT)):
			if MAX_NODES_COUNT[i] == -1 or current_node_counts[i] < MAX_NODES_COUNT[i]:
				available_node_types.append(i)

		c = choice(available_node_types)
		current_node_counts[c] += 1
		board[ox][oy] = Node(ox, oy, c, False)

		# add it to the stack
		shuffle(Directions)
		stack.append((nx, ny, list(Directions)))

	# set goal node
	goal_x, goal_y = L//2, H//2
	middle_cell_old_value = board[goal_x][goal_y]
	board[goal_x][goal_y] = Node(goal_x, goal_y, len(NODE_DISPLAY_CODES) - 1, True)

	# if ancient cell was not a node (it was a Link or None), there will be a connection
	# problem after replacement: we need to create a small pattern around the goal node
	# to force connection by adding rows/columns and creating links
	# ----------------------
	# if old cell was a Link
	if middle_cell_old_value.__class__.__name__ == 'Link':
		# if old cell was a horizontal link
		if middle_cell_old_value.direction == 0:
			# remember links in this column that will be cut later
			links_in_column = []
			for y in range(H):
				if board[goal_x][y].__class__.__name__ == 'Link' and board[goal_x][y].direction == 0:
					links_in_column.append(y)

			# insert columns around the goal node to create space for new links
			board.insert(goal_x, [None] * H);
			board.insert(goal_x+2, [None] * H);
			L += 2
			goal_x += 1

			# place nodes to replace cut off links and add links around them in the newly created columns
			for y in range(H//2):
				if y in links_in_column:
					board[goal_x-1][y] = Link(0)
					board[goal_x][y] = Node(goal_x, y, randint(0, NODE_TYPES), False)
					board[goal_x+1][y] = Link(0)

			# add the goal node links
			board[goal_x-1][goal_y] = Link(0)
			board[goal_x+1][goal_y] = Link(0)			

		# else if old cell was a vertical link
		elif middle_cell_old_value.direction == 1:
			# remember links in this row that will be cut later
			links_in_row = []
			for x in range(L):
				if board[x][goal_y].__class__.__name__ == 'Link' and board[x][goal_y].direction == 1:
					links_in_row.append(x)

			# insert rows around the goal node to create space for new links
			for x in range(L):
				board[x].insert(goal_y, None);
				board[x].insert(goal_y+2, None);
			H += 2
			goal_y += 1

			# place nodes to replace cut off links and add links around them in the newly created rows
			for x in range(L//2):
				if x in links_in_row:
					board[x][goal_y-1] = Link(1)
					board[x][goal_y] = Node(x, goal_y, randint(0, NODE_TYPES - 1), False)
					board[x][goal_y+1] = Link(1)

			# add the goal node links
			board[goal_x][goal_y-1] = Link(1)
			board[goal_x][goal_y+1] = Link(1)
	# if old cell was null			
	elif middle_cell_old_value is None:
		links_in_row = []
		for x in range(L):
			if board[x][goal_y].__class__.__name__ == 'Link' and board[x][goal_y].direction == 1:
				links_in_row.append(x)

		for x in range(L):
			board[x].insert(goal_y, None);
			board[x].insert(goal_y+2, None);
		H += 2
		goal_y += 1

		# place nodes to replace cut off links and add links around them in the newly created rows
		for x in range(L//2):
			if x in links_in_row:
				board[x][goal_y-1] = Link(1)
				board[x][goal_y] = Node(x, goal_y, randint(0, NODE_TYPES - 1), False)
				board[x][goal_y+1] = Link(1)

		# add the goal node links
		board[goal_x][goal_y-1] = Link(1)
		board[goal_x][goal_y+1] = Link(1)

	# symmetrize the board: central symmetry around middle point
	for x in range(L):
		for y in range(H):
			if type(board[x][y]) == Node:
				board[L-1-x][H-1-y] = Node(L-1-x, H-1-y, board[x][y].type, board[x][y].isGoal)
			elif type(board[x][y]) == Link:
				board[L-1-x][H-1-y] = Link(board[x][y].direction)

	# create a random 'cutename' for the Board (one that can be displayed in the server)
	nameparts1 = ['Black', 'Red', 'Blue', 'Green', 'New', 'Old', 'Disconnected', 'Unique', 'Estranged']
	nameparts2 = ['Network', 'Grid', 'Cells', 'Web', 'Server', 'Router', 'Antenna', 'Satellite']
	r = randint(0, 100)
	if r < 20:
		name = choice(nameparts2) + ' '
		name += choice(['X', 'Y', 'Z', 'Theta', 'Omega', 'Alpha']) + '-' + str(randint(10, 30))
	else:
		name = choice(nameparts1) + ' ' + choice(nameparts2)

	return L, H, board, name, board[goal_x][goal_y]


class Networks(Game):
	"""
	class Networks

	Inherits from Game
	- _players: tuple of the two players
	- _logger: logger to use to log infos, debug, ...
	- _name: name of the game
	- _whoPlays: number of the player who should play now (0 or 1)
	- _waitingPlayer: Event used to wait for the players
	- _lastMove, _last_return_code: string and returning code corresponding to the last move

	Custom properties:
	- _board: array (list of lists of integers) representing the board
	- _L, _H: length and height of the board
	- _goalNode: reference to the goal node in the middle of the board
	- _playerNode: list of the nodes of the two players
	- _inCaptureNode: list of the currently in-capture nodes if the two players
	- _playerEnergy: list of the energy level of the two players
	- _cutename: 'cutename' of the board (for server display of the game)
	"""

	# dictionary of the possible training Players (name-> class)
	type_dict = {"DO_NOTHING": DoNothingPlayer,
				 "ALICE_RANDOM": AliceRandomPlayer,
				 "WHITE_RABBIT": WhiteRabbitPlayer,
				 "NEO": NeoPlayer,
				}


	def __init__(self, player1, player2, **options):
		"""
		Create a game
		:param player1: 1st Player
		:param player2: 2nd Player
		:param options: dictionary of options (the options 'seed' and 'timeout' are managed by the Game class)
		"""

		# random Board, cutename and goalNode
		#self._L, self._H, self._board, self._cutename, self._goalNode = CreateBoard(randint(4, 6), randint(4, 6))
		self._L, self._H, self._board, self._cutename, self._goalNode = CreateBoard(2, 2)

		# add players
		self._playerNode = [[], []]  # two lists of nodes
		self._inCaptureNode = [[], []]	# two lists of nodes

		# level of energy
		self._playerEnergy = [0] * 2

		# capture opposite corners nodes for each player
		start_nodes = [(0, 0), (self._L-1, self._H-1)]
		for i, e in enumerate(start_nodes):
			x, y = e
			self._board[x][y].capture(i)
			self._playerNode[i].append(self._board[x][y])

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
	def playerNode(self):
		"""Returns the positions of the players owned nodes"""
		return self._playerNode

	@property
	def inCaptureNodes(self):
		"""Returns the nodes currently in-capture for both players"""
		return self._inCaptureNode

	@property
	def playerEnergy(self):
		"""Returns the energy of the players"""
		return self._playerEnergy

	@property
	def goalNode(self):
		"""Returns the reference to goal node (middle of the board)"""
		return self._goalNode

	@property
	def currentPlayer(self):
		"""Returns the index of the player currently playing"""
		return self._whoPlays

	@property
	def board(self):
		"""Returns the board"""
		return self._board

	def HTMLrepr(self):
		"""Returns an HTML representation of the game"""
		return "<a href='/game/%s'>%s</a>" % (self.name, self._cutename)

	def getDictInformations(self):
		"""
		Returns a dictionary for HTML display
		:return:
		"""
		# conv = Ansi2HTMLConverter()
		# html = conv.convert(str(self))
		# for code in NODE_DISPLAY_CODES:
		# 	for c in code:
		# 		html = html.replace(c, 'x')

		values = []
		for y in range(self.H):
			for x in range(self.L):
				if self.board[x][y] is None:
					values.append('')
				else:
					values.append(self.board[x][y].display_html())

		return {'width': self.L, 'values': values, 'energy': self._playerEnergy, 'curPlayerId': self._whoPlays}

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
			lines.append(colors[i] + br[0] + "Player " + str(i + 1) + ": " + Fore.RESET + pl.name.rjust(20) + colors[i] + "\t\tEnergy: " + str(self._playerEnergy[i]) + br[1] + Fore.RESET)

		# display board
		for y in range(self.H):
			st = []
			for x in range(self.L):
				# add blank cell
				if self.board[x][y] is None:
					st.append(" ")
				# or display element according to its display function
				else:
					st.append(self.board[x][y].display_str())
			lines.append("|" + "".join(st) + "|")

		head = "+" + "-" * (self._L) + "+\n"
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

		# parse the move: the move contains the type, then x, y coordinates
		result = regdd.match(move)
		# check if the data receive is valid
		if result is None:
			return LOSING_MOVE, "The move is not in correct form ('%d %d %d') !"
		# get the type and the value
		move_type = int(result.group(1))
		move_x = int(result.group(2))
		move_y = int(result.group(3))
		if not (CAPTURE <= move_type <= DO_NOTHING):
			return LOSING_MOVE, "The type is not valid !"
		if move_x < 0 or move_x >= self.L:
			return LOSING_MOVE, "The x coordinate is not valid!"
		if move_y < 0 or move_y >= self.H:
			return LOSING_MOVE, "The y coordinate is not valid!"

		# update in-capture nodes
		for i in range(len(self._playerNode)):
			for n in self._inCaptureNode[i]:
				if n.check_capture(self._playerNode[i], self._inCaptureNode[i]) and n.isGoal:
					if i == self._whoPlays:
						return WINNING_MOVE, "Captured goal node!"
					else:
						return LOSING_MOVE, "Opponent captured goal node!"

		# capture node
		if move_type == CAPTURE:
			if not type(self.board[move_x][move_y]) == Node:
				return LOSING_MOVE, "Cannot capture, not a node!"
			#if self.board[move_x][move_y].owner == self._whoPlays:
			if self.board[move_x][move_y].owner >= 0 :
				return LOSING_MOVE, "Cannot re-capture an already-owned node!"


			# check if there are neighbours owned by current player
			neighbours_count = 0
			for node in self._playerNode[self._whoPlays]:
				x, y = node.x, node.y
				if x == move_x:
					if move_y - y == 2 and \
						(type(self.board[x][y+1]) == Link and self.board[x][y+1].direction == 1):
						neighbours_count += 1
					elif move_y - y == -2 and \
						(type(self.board[x][y-1]) == Link and self.board[x][y-1].direction == 1):
						neighbours_count += 1
				elif y == move_y:
					if move_x - x == 2 and \
						(type(self.board[x+1][y]) == Link and self.board[x+1][y].direction == 0):
						neighbours_count += 1
					elif move_x - x == -2 and \
						(type(self.board[x-1][y]) == Link and self.board[x-1][y].direction == 0):
						neighbours_count += 1
			# if no OK neighbours, losing move
			if neighbours_count == 0:
				return LOSING_MOVE, "No owned neighbour node, impossible to link!"
			# else set node capture
			self.board[move_x][move_y].set_capture(self._whoPlays, self._inCaptureNode[self._whoPlays])

			# update energy
			self._playerEnergy[self._whoPlays] += 1

			return NORMAL_MOVE, ""

		elif move_type == DO_NOTHING:
			# update player energy
			self._playerEnergy[self._whoPlays] += 1
			return NORMAL_MOVE, ""

		# destroy link between nodes
		elif move_type == DESTROY:
			# check for energy level
			if self._playerEnergy[self._whoPlays] < DESTROY_ENERGY:
				return LOSING_MOVE, "Not enough energy to destroy a link."

			# check for non link cell
			if not type(self.board[move_x][move_y]) == Link:
				return LOSING_MOVE, "Not a link, cannot destroy."
			# else, remove link (make blank cell)
			self.board[move_x][move_y] = None

			# update energy
			self._playerEnergy[self._whoPlays] -= DESTROY_ENERGY

			return NORMAL_MOVE, ""

		# create new horizontal link between nodes
		elif move_type == LINK_H:
			# check for energy level
			if self._playerEnergy[self._whoPlays] < LINK_ENERGY:
				return LOSING_MOVE, "Not enough energy to create a link."

			# check for non empty cell
			if self.board[move_x][move_y]:
				return LOSING_MOVE, "Cannot build link here, cell is already occupied."
			# check for neighbours
			if not type(self.board[move_x-1][move_y]) == Node or \
				not type(self.board[move_x+1][move_y]) == Node:
				return LOSING_MOVE, "No nodes to link here!"
			# if everything is OK, add link
			self.board[move_x][move_y] = Link(0)

			# update energy
			self._playerEnergy[self._whoPlays] -= LINK_ENERGY

			return NORMAL_MOVE, ""

		# create new vertical link between nodes
		elif move_type == LINK_V:
			# check for energy level
			if self._playerEnergy[self._whoPlays] < LINK_ENERGY:
				return LOSING_MOVE, "Not enough energy to create a link."

			# check for non empty cell
			if self.board[move_x][move_y]:
				return LOSING_MOVE, "Cannot build link here, cell is already occupied."
			# check for neighbours
			if not type(self.board[move_x][move_y-1]) == Node or \
				not type(self.board[move_x][move_y+1]) == Node:
				return LOSING_MOVE, "No nodes to link here!"
			# if everything is OK, add link
			self.board[move_x][move_y] = Link(1)

			# update energy
			self._playerEnergy[self._whoPlays] -= LINK_ENERGY

			return NORMAL_MOVE, ""

		return NORMAL_MOVE, ""

	def getDataSize(self):
		"""
		Returns the size of the next incoming data
		"""
		return "%d %d" % (self.L, self.H)

	def getCutename(self):
		"""
		Returns the cutename of the game (to display in html views)
		"""
		if hasattr(self, '_cutename'):
			return self._cutename
		else:
			return None


	def getData(self):
		"""
		Return the data of the game (when ask with the GET_GAME_DATA message)
		Only takes into account the view window (not the entire board)
		"""
		msg = []
		for y in range(self.H):
			for x in range(self.L):
					if type(self._board[x][y]) == Node:
						msg.append(str(3+self._board[x][y].type))
					elif type(self._board[x][y]) == Link:
						msg.append(str(self._board[x][y]))
					else:
						msg.append('0')

		self.logger.debug(msg)
		return "".join(msg)

	def getNextPlayer(self):
		"""
		Change the player who plays
		Returns the next player (but do not update self._whoPlays)
		"""
		return 1 - self._whoPlays       # in a tour-by-tour game, it's the opponent to play

