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
from random import choice


class PlayRandomPlayer(Player):

	def __init__(self):
		super().__init__('Play_Random')


	def playMove(self):
		"""
		Plays the move -> here a random move
		Returns the move (string %d %d)
		"""
		# build the list of the possible moves

		moves = ["%d 0" % (x,) for x in range(9)]

		# choose one
		return choice(moves)

