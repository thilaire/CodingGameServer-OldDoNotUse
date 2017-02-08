"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev...

File: League.py
	Contains the League class
	-> defines the behavior of a league tournament

"""


from server.Tournament import Tournament, numbering


class League(Tournament):
	"""
	League mode
	"""
	mode = "League"
	HTMLoptions = ""


	def __init__(self, name, nbMaxPlayers, nbRounds4Victory, **_):        # **_ stands for the unused other parameters...
		# call the super class constructor
		super().__init__(name, nbMaxPlayers, nbRounds4Victory)

		# initial score (empty for the moment, we don't know the players)
		self._score = {}


	def MatchsGenerator(self):
		"""
		Generator that generate, for each phase, a tuple:
		- the name of the phase
		- a list of players who will play together
		(a list of 2-tuples (name1,name2), where name1 and name2 are the names of the players who will play together)

		At the end, set the winner

		It uses the round robin tournament algorithm to generate the matches of each phase
		see http://en.wikipedia.org/wiki/Round-robin_tournament and
		http://stackoverflow.com/questions/11245746/league-fixture-generator-in-python/11246261#11246261
		"""
		# score (indexed by players' name)
		self._score = {pName: 0 for pName in self.players.keys()}

		# copy the player list
		rotation = list(self._players.keys())
		# if player number is odd, we use "" as a fake player
		if len(rotation) % 2:
			rotation.append("")

		# then we iterate using round robin algorithm
		for i in range(0, len(rotation) - 1):
			# update the phase name
			phase = '%d%s phase' % (i+1, numbering(i+1))
			# generate list of pairs (player1,player2)
			yield phase, list(zip(*[iter(rotation)] * 2))
			# prepare the next list by rotating the list
			rotation = [rotation[0]] + [rotation[-1]] + rotation[1:-1]

		# end of the tournament
		# !FIXME: who wins when equality ??
		self._winner = max(self._score, key=lambda key: self._score[key])

	def updateScore(self):
		"""
		update the score from the dictionary of games runned in that phase
		Called by runPhase at the end of each phase
		"""
		for (p1, p2), (score, _) in self._games.items():
			if score[0] > score[1]:
				self._score[p1] += 1
			else:
				self._score[p2] += 1


	def HTMLscore(self):
		"""
		Display the actual score

		Returns a HTML string
		"""
		if self._score:
			return "<ul>"+"".join("<li>%s: %d points</li>" % (self.playerHTMLrepr(pName), score)
				                      for pName, score in self._score.items())+"</ul>"
		else:
			return ""

