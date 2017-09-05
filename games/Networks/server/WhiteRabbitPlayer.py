"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: M. Pecheux (based on J. Brajard template file)
Licence: GPL

File: WhiteRabbitPlayer.py
	Contains the class WhiteRabbitPlayer
	-> defines a player that uses Astar algorithm to move along the shortest path
	(but do not use any special action like link creation/destruction)

Copyright 2017 M. Pecheux
"""

from server.Player import TrainingPlayer
from .Constants import CAPTURE, DO_NOTHING

boolConv = {'true': True, 'false': False}


def check_type(element, typecheck):
	"""Function that checks for class type (class is not yet
	defined, so cannot use type() built-in...)"""
	return element is not None and element.__class__.__name__ == typecheck


class WhiteRabbitPlayer(TrainingPlayer):
	"""
	class WhiteRabbitPlayer that create Astar training players

	-> this player do not consider special actions, and move only along the shortest path
	(found with a A* algorithm)
	see https://en.wikipedia.org/wiki/A*_search_algorithm
	"""

	def __init__(self, **_):
		super().__init__('WHITE RABBIT')

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
			if check_type(n, "Node") and (n.isGoal or n.owner != us) and \
				not (n in self.game.inCaptureNodes[us]) and \
				check_type(l, "Link") and l.direction == 0:
				neighbours.append(n)
		if x < self.game.L-2:
			n = self.game.board[x+2][y]
			l = self.game.board[x+1][y]
			if check_type(n, "Node") and (n.isGoal or n.owner != us) and \
				not (n in self.game.inCaptureNodes[us]) and \
				check_type(l, "Link") and l.direction == 0:
				neighbours.append(n)
		if y > 1:
			n = self.game.board[x][y-2]
			l = self.game.board[x][y-1]
			if check_type(n, "Node") and (n.isGoal or n.owner != us) and \
				not (n in self.game.inCaptureNodes[us]) and \
				check_type(l, "Link") and l.direction == 1:
				neighbours.append(n)
		if y < self.game.H-2:
			n = self.game.board[x][y+2]
			l = self.game.board[x][y+1]
			if check_type(n, "Node") and (n.isGoal or n.owner != us) and \
				not (n in self.game.inCaptureNodes[us]) and \
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

		# build the grid of distances
		delta = [list((-1,) * self.game.H) for _ in range(self.game.L)]
		delta[self.game.goalNode.x][self.game.goalNode.y] = 0

		loop = True

		# Loop if data are style to explore
		d = 0
		while loop:
			loop = False
			min_node_add = 3
			# one in two cells (avoid the link cells)
			for x in range(0, self.game.L, 2):
				for y in range(0, self.game.H, 2):
					if delta[x][y] == d:
						for n in self.neighbours(x, y, us):
							if check_type(self.game.board[n.x][n.y], "Node") and \
								delta[n.x][n.y] == -1:
								loop = True
								delta[n.x][n.y] = d+(n.type+1)
								if n.type+1 < min_node_add:
									min_node_add = n.type+1
			d += min_node_add

		# print('>> GOT DELTA ARRAY')
		# o = '\n'
		# for y in range(self.game.H):
		# 	for x in range(self.game.L):
		# 		o += '%02d ' % delta[x][y]
		# 	o += '\n'
		# print(o)

		# Find the best move
		moves = dict()
		for node in self.game.playerNode[us]:
			x, y = node.x, node.y
			for n in self.neighbours(x, y, us):
				if delta[n.x][n.y] != -1:
					moves[(n.x, n.y)] = delta[n.x][n.y]

		if moves:
			bestmove_x, bestmove_y = min(moves, key=moves.get)
			return "%d %d %d" % (CAPTURE, bestmove_x, bestmove_y)
		else:
			if (len(self.game.inCaptureNodes[us]) == 0):
				self.game.sendComment(self, "I am blocked... I cannot move... Aaarg! You got me!!")
			else:
				self.game.sendComment(self, "I am coming to get you...!!")
			return "%d 0 0" % DO_NOTHING
