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

from CGS.Player import Player
from random import choice, randint
from .Constants import MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, MOVE_UP, ROTATE_COLUMN_DOWN, ROTATE_COLUMN_UP, ROTATE_LINE_LEFT, ROTATE_LINE_RIGHT, ROTATE_ENERGY
from .Constants import Ddx, Ddy

class PlayRandomPlayer(Player):

	def __init__(self):
		super().__init__('Play_Random')


	def playMove(self):
		"""
		Plays the move -> here a random move
		Returns the move (string %d %d)

		A non-regular player is player #1 (the opponent is #0)

		"""
		# build the list of the possible moves
		moves = []

		# move
		for move_type in ( MOVE_UP , MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT):
			x, y = self.game._playerPos[1]
			x = (x + Ddx[move_type]) % self.game.L
			y = (y + Ddy[move_type]) % self.game.H

			if self.game._lab[x][y]:
				moves.append("%d 0"%move_type)

		# rotate line or column
		if self.game._playerEnergy[1] >= ROTATE_ENERGY:
			line = randint(0,self.game.H)
			col = randint(0, self.game.L)
			moves.append("%d %d" % (ROTATE_COLUMN_DOWN, col) )
			moves.append("%d %d" % (ROTATE_COLUMN_UP, col) )
			moves.append("%d %d" % (ROTATE_LINE_RIGHT, line) )
			moves.append("%d %d" % (ROTATE_LINE_LEFT, line) )

		# choose one (up to 4 moves and 4 rotations)
		return choice(moves)

