"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev...

File: playRandomPlayer.py
	Contains the class playRandomPlayer
	-> defines a dummy player that play randomly every time (but do not loose)
"""

from CGS.Player import TrainingPlayer
from random import choice, randint
from .Constants import MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, MOVE_UP, DO_NOTHING
from .Constants import ROTATE_COLUMN_DOWN, ROTATE_COLUMN_UP, ROTATE_LINE_LEFT, ROTATE_LINE_RIGHT, ROTATE_ENERGY
from .Constants import Ddx, Ddy

boolConv = {'true': True, 'false': False}


class PlayRandomPlayer(TrainingPlayer):

	def __init__(self, **options):
		super().__init__('Play_Random')

		# check "rotate" option
		if "rotate" not in options:
			self.rotate = True
		elif options["rotate"].lower() in boolConv:
			self.rotate = boolConv[options["rotate"].lower()]
		else:
			raise ValueError("The option rotate=%s is incorrect." % options["rotate"])


	def playMove(self):
		"""
		Plays the move -> here a random move
		Returns the move (string %d %d)
		"""
		# get our player number
		us = 0 if (self.game.players[0] is self) else 1

		# build the list of the possible moves
		moves = []

		# move
		for move_type in (MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT):
			x, y = self.game.playerPos[us]
			x = (x + Ddx[move_type]) % self.game.L
			y = (y + Ddy[move_type]) % self.game.H

			if self.game.lab[x][y]:
				moves.append("%d 0" % move_type)

		# rotate line or column
		if self.game.playerEnergy[us] >= ROTATE_ENERGY and self.rotate:
			line = randint(0, self.game.H-1)
			col = randint(0, self.game.L-1)
			moves.append("%d %d" % (ROTATE_COLUMN_DOWN, col))
			moves.append("%d %d" % (ROTATE_COLUMN_UP, col))
			moves.append("%d %d" % (ROTATE_LINE_RIGHT, line))
			moves.append("%d %d" % (ROTATE_LINE_LEFT, line))

		# choose one (up to 4 moves and 4 rotations)
		if moves:
			return choice(moves)
		else:
			# sometimes, we cannot move...
			self.game.sendComment(self, "I am blocked... I cannot move...")
			return "%d 0" % DO_NOTHING

