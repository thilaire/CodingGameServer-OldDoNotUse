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

from server.Player import TrainingPlayer
from .Constants import DO_NOTHING


class DoNothingPlayer(TrainingPlayer):
	"""
	This class defines a stupid training player that does... nothing
	(it plays DO_NOTHING every time)
	It is used for the first part of the project (players need an opponent that does nothing to check their	code)
	"""

	def __init__(self, **_):
		"""Initialize the Training Player
		no options, nothing to do with options
		"""
		super().__init__('Do_nothing')


	def playMove(self):
		"""
		Plays the move -> here DO_NOTHING
		Returns the move (string %d %d)
		"""
		return "%d 0" % DO_NOTHING

