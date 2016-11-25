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

from CGS.Player import Player
from .Constants import DO_NOTHING


class DoNothingPlayer(Player):

	def __init__(self, **options):
		super().__init__('Do_nothing')

		# no options, so nothing to do with options

	# static method, just because this dummy player does nothing (and does not use `self`)
	@staticmethod
	def playMove():
		"""
		Plays the move -> here DO_NOTHING
		Returns the move (string %d %d)
		"""
		return "%d 0" % DO_NOTHING

