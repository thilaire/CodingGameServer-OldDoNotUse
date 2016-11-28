"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev...

File: DoNothingPlayer.py
	Contains the class DoNothingPlayer
	-> defines a stupid player that does... nothing (it plays DO_NOTHING every time)

"""

from CGS.Player import TrainingPlayer
from .Constants import DO_NOTHING


class DoNothingPlayer(TrainingPlayer):

	# noinspection PyUnusedLocal
	def __init__(self, **options):
		super().__init__('Do_nothing')

		# no options, so nothing to do with options


	def playMove(self):
		"""
		Plays the move -> here DO_NOTHING
		Returns the move (string %d %d)
		"""
		return "%d 0" % DO_NOTHING

