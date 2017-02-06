"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev...

File: SimpleElimination.py
	Contains the SingleElimination class
	-> defines the behavior of a single-elimination tournament
	see https://en.wikipedia.org/wiki/Single-elimination_tournament

"""

from CGS.Tournament import Tournament



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
