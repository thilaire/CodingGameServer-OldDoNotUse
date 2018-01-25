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
from .Constants import CAPTURE, DESTROY, LINK_H, LINK_V, DO_NOTHING

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
		self.path = []		# a* path for the AI, i.e. list of coordinates tuples (the nodes left to capture)
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

	def getDistanceGrid(self, us, start):
		# build the grid of distances to the goal node
		delta = [list((-1,) * self.game.H) for _ in range(self.game.L)]
		delta[start[0]][start[1]] = 0

		loop = True

		# Loop if data are style to explore
		new_deltas = {start: 0}
		checked = []
		while len(new_deltas) > 0:
			bestDelta = min(new_deltas, key=new_deltas.get)
			x, y = bestDelta
			d = new_deltas.pop(bestDelta)

			for n in self.neighbours(x, y, us):
				if check_type(self.game.board[n.x][n.y], "Node") and \
						delta[n.x][n.y] == -1:
					delta[n.x][n.y] = d+(n.type+1)
					new_deltas[(n.x, n.y)] = d+(n.type+1)
					checked.append((n.x, n.y))

		return delta

	def getDistance(self, delta, us, start, end):
		distance = 0
		current = start

		while current != end:
			x, y = current[0], current[1]
			minDist = 1000
			minNeighbour = (-1, -1)
			for n in self.neighbours(x, y, us):
				if delta[n.x][n.y] != -1 and delta[n.x][n.y] < minDist:
					minDist = delta[n.x][n.y]
					minNeighbour = (n.x, n.y)

			if minNeighbour == (-1, -1):
				print ('Incorrect A* distance computing. Aborting.')
				return -1

			distance += minDist
			current = minNeighbour

		return distance

	def getBestNeighbour(self, delta, us, capturedNodes):
		neighbours = {}
		for node in capturedNodes:
			x, y = node.x, node.y
			for n in self.neighbours(x, y, us):
				if delta[n.x][n.y] != -1:
					neighbours[(n.x, n.y)] = delta[n.x][n.y]

		if neighbours:
			return min(neighbours, key=neighbours.get)
		else:
			return None

	def computePath(self, us):
		# build the grid of distances to the goal node
		deltaF = self.getDistanceGrid(us, (self.game.goalNode.x, self.game.goalNode.y))

		openSet = []
		closedSet = []
		bestPrevious = {}
		capturedNodes = self.game.playerNode[us] + self.game.inCaptureNodes[us]
		end = (self.game.goalNode.x, self.game.goalNode.y)
                
		BestNeighbour = self.getBestNeighbour(deltaF, us, capturedNodes)
		if BestNeighbour is None:
			return []
		openSet.append(BestNeighbour)

		# build the grid of distances to the start node
		deltaG = self.getDistanceGrid(us, openSet[0])

		# print('>> F SCORE ARRAY (to goal)')
		# o = '\n'
		# for y in range(self.game.H):
		# 	for x in range(self.game.L):
		# 		if self.game.board[x][y] is None:
		# 			o += '   '
		# 		else:
		# 			o += '%02d ' % deltaF[x][y]
		# 	o += '\n'
		# print(o)

		# print('>> G SCORE ARRAY (to start)')
		# o = '\n'
		# for y in range(self.game.H):
		# 	for x in range(self.game.L):
		# 		if self.game.board[x][y] is None:
		# 			o += '   '
		# 		else:
		# 			o += '%02d ' % deltaG[x][y]
		# 	o += '\n'
		# print(o)

		while len(openSet) > 0:
			current = min(openSet, key=lambda t: deltaF[t[0]][t[1]])
			if current == end:
				return self.reconstructPath(bestPrevious, current)

			openSet.remove(current)
			closedSet.append(current)

			x, y = current[0], current[1]
			for n in self.neighbours(x, y, us):
				neighbour = (n.x, n.y)
				if neighbour in closedSet:
					continue

				if neighbour not in openSet:
					openSet.append(neighbour)

				comparedGScore = 100
				if neighbour in bestPrevious.keys():
					comparedGScore = deltaG[bestPrevious[neighbour][0]][bestPrevious[neighbour][1]]
				if deltaG[n.x][n.y] >= comparedGScore:
					continue

				bestPrevious[neighbour] = current

		return []

	def reconstructPath(self, bestPrevious, current):
		path = [current]
		while current in bestPrevious.keys():
			current = bestPrevious[current]
			path.append(current)

		return path

	def playMove(self):
		"""
		Plays the move -> here an A* equivalent move (best way to get closer to goal node)
		Returns the move (string %d %d %d)
		"""

		# get our player number
		us = 0 if (self.game.players[0] is self) else 1

		opponentMoveType = self.game._lastMove.split(' ')[0]
		if opponentMoveType != '':
			opponentMoveType = int(opponentMoveType)
		else:
			opponentMoveType = -1

		# if there is no current path or the board has changed and the AI is
		# not capturing the goal node, try to compute a new path
		if (len(self.path) == 0 or opponentMoveType in [DESTROY, LINK_H, LINK_V]) \
				and self.game.goalNode not in self.game.inCaptureNodes[us]:
			self.path = self.computePath(us)

		# if path is still null after computing:
		# - there is no way to the goal
		# - the goal is currently in-capture
		if len(self.path) == 0:
			if self.game.goalNode not in self.game.inCaptureNodes[us]:
				self.game.sendComment(self, "I am blocked... I cannot move... Aaarg! You got me!!")
			else:
				self.game.sendComment(self, "The White Rabbit has tumbled down the hole... loser!!")
			return "%d 0 0" % DO_NOTHING
		# else if path is possible but node is currently in-capture, wait for capture to complete
		elif (len(self.game.inCaptureNodes[us]) != 0):
			self.game.sendComment(self, "The White Rabbit is on its way to Wonderland!!")
			return "%d 0 0" % DO_NOTHING
		# else start capture of next node in path
		else:
			next_node = self.path.pop()
			return "%d %d %d" % (CAPTURE, next_node[0], next_node[1])
