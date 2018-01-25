"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: M. Pecheux (based on T. Hilaire and J. Brajard template file)
Licence: GPL

File: DoNothingPlayer.py
	Contains the class DoNothingPlayer
	-> defines a stupid player that does... nothing (it plays DO_NOTHING every time)

Copyright 2017 M. Pecheux
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
		super().__init__('DO NOTHING')


	def playMove(self):
		"""
		Plays the move -> here DO_NOTHING
		Returns the move (string %d %d %d)
		"""
		return "%d 0 0" % DO_NOTHING

