"""
* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL

File: SimpleElimination.py
	Contains the SingleElimination class
	-> defines the behavior of a single-elimination tournament
	see https://en.wikipedia.org/wiki/Single-elimination_tournament

Copyright 2016-2017 T. Hilaire, J. Brajard
"""

from server.Tournament import Tournament



class SingleEliminationTournament(Tournament):
	"""
	Single-elimination tournament
	https://en.wikipedia.org/wiki/Single-elimination_tournament
	"""
	mode = "Single-elimination Tournament"
	HTMLoptions = ""

	def __init__(self, name, nbMaxPlayers, nbRounds4victory, **_):
		# call the super class constructor
		super().__init__(name, nbMaxPlayers, nbRounds4victory)

	# NOTIMPLEMENTED
