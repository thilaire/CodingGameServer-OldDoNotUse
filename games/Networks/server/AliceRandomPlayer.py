"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: M. Pecheux (based on T. Hilaire and J. Brajard template file)
Licence: GPL

File: aliceRandomPlayer.py
	Contains the class aliceRandomPlayer
	-> defines a dummy Alice player that play randomly every time (but do not loose)

Copyright 2017 M. Pecheux
"""

from server.Player import TrainingPlayer
from random import choice, randint
from .Constants import CAPTURE, DESTROY, LINK_H, LINK_V, DO_NOTHING, \
	LINK_ENERGY, DESTROY_ENERGY

boolConv = {'true': True, 'false': False}


def check_type(element, typecheck):
	"""Function that checks for class type (class is not yet
	defined, so cannot use type() built-in...)"""
	return element is not None and element.__class__.__name__ == typecheck


class AliceRandomPlayer(TrainingPlayer):
	"""
	This class implements Alice: a training player that plays... randomly
	Every player should be able to beat him
	"""
	def __init__(self, **options):
		"""
		Initialize the training player
		The option "advanced=true" (default) or "advanced=false" is possible
		This option indicates if the player can also destroy/create links
		"""
		super().__init__('ALICE')

		# check "advanced" option
		if "advanced" not in options:
			self.advanced = True
		elif options["advanced"].lower() in boolConv:
			self.advanced = boolConv[options["advanced"].lower()]
		else:
			raise ValueError("The option advanced=%s is incorrect." % options["advanced"])

	def neighbours(self, x, y, us):
		"""
		:param x: coordinate of a point
		:param y: coordinate of a point
		:return: list of neighbours of the point (x,y)
		"""
		neighbours = []

		if x > 1:
			n = self.game.board[x-2][y]
			l = self.game.board[x-1][y]
			if check_type(n, "Node") and ( n.owner != us) and \
				check_type(l, "Link") and l.direction == 0:
				neighbours.append(n)
		if x < self.game.L-2:
			n = self.game.board[x+2][y]
			l = self.game.board[x+1][y]
			if check_type(n, "Node") and (n.owner != us) and \
				check_type(l, "Link") and l.direction == 0:
				neighbours.append(n)
		if y > 1:
			n = self.game.board[x][y-2]
			l = self.game.board[x][y-1]
			if check_type(n, "Node") and (n.owner != us) and \
				check_type(l, "Link") and l.direction == 1:
				neighbours.append(n)
		if y < self.game.H-2:
			n = self.game.board[x][y+2]
			l = self.game.board[x][y+1]
			if check_type(n, "Node") and (n.owner != us) and \
				check_type(l, "Link") and l.direction == 1:
				neighbours.append(n)

		return neighbours

	def playMove(self):
		"""
		Plays the move -> here a random move
		Returns the move (string %d %d %d)
		"""
		# get our player number
		us = 0 if (self.game.players[0] is self) else 1

		# build the list of the possible moves
		moves = []

		# capture node
		# get currently owned nodes neighbours and add them to the moved list
		for node in self.game.playerNode[us]:
			for n in self.neighbours(node.x, node.y, us):
				moves.append("%d %d %d" % (CAPTURE, n.x, n.y))

		# advanced moves
		if self.advanced:
			# destroy link
			if self.game.playerEnergy[us] >= DESTROY_ENERGY:
				linkCells = [(x,y) for x in range(self.game.L-1) for y in range(self.game.H-1) if check_type(self.game.board[x][y], "link")]
				if len(linkCells) > 0:
					lx, ly = choice(linkCells)
					moves.append("%d %d %d" % (DESTROY, lx, ly))
			# create link
			if self.game.playerEnergy[us] >= LINK_ENERGY:
				blankCells = []
				for x in range(1, self.game.L-1):
					for y in range(1, self.game.H-1):
						if self.game.board[x][y] is None:
							if check_type(self.game.board[x-1][y], "Node") and \
								check_type(self.game.board[x+1][y], "Node"):
								blankCells.append((x, y, 0))
							elif check_type(self.game.board[x][y-1], "Node") and \
								check_type(self.game.board[x][y+1], "Node"):
								blankCells.append((x, y, 1))
				if len(blankCells) > 0:
					cx, cy, d = choice(blankCells)
					if d == 0:
						moves.append("%d %d %d" % (LINK_H, cx, cy))
					elif d == 1:
						moves.append("%d %d %d" % (LINK_V, cx, cy))

		# choose one possible move
		if moves:
			return choice(moves)
		else:
			# sometimes, we cannot move...
			self.game.sendComment(self, "I am blocked... I cannot play...")
			return "%d 0 0" % DO_NOTHING

