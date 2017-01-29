"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev...

File: Mode.py
	Contains some subclasses of the class Tournament
	-> defines the different tournaments behavior

"""


from CGS.Tournament import Tournament

# TODO: put them in different files ?


def numbering(i):
	if i == 1:
		return 'st'
	elif i == 2:
		return 'nd'
	elif i == 3:
		return 'rd'
	else:
		return 'th'


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
		Use the round robin tournament algorithm
		see http://en.wikipedia.org/wiki/Round-robin_tournament and
		http://stackoverflow.com/questions/11245746/league-fixture-generator-in-python/11246261#11246261
		"""
		# score
		self._score = {p: 0 for p in self.players}

		# copy the player list
		# TODO: vérifier s'ils sont tous encore là ?
		rotation = list(self._players)
		# if player number is odd, we use None as a fake player
		if len(rotation) % 2:
			rotation.append(None)

		# then we iterate using round robin algorithm
		for i in range(0, len(rotation) - 1):
			# update the phase name
			self._phase = '%d%s phase' % (i+1, numbering(i+1))
			# generate list of pairs (player1,player2)
			yield list(zip(*[iter(rotation)] * 2))
			# prepare the next list by rotating the list
			rotation = [rotation[0]] + [rotation[-1]] + rotation[1:-1]

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
			return "<ul>"+"".join("<li>%s: %d points</li>" % (p.HTMLrepr(), score) for p, score in self._score.items())+"</ul>"
		else:
			return ""



class PoolKnockoutTournament(Tournament):
	mode = "Two stages (pool + knockout) Tournament"
	HTMLoptions = """
	<label>
		Nb groups: <input name="nbGroups" type="number" value="4" required/>
	</label>
	<br/>
	<label>
		Nb of players per group that can pass the first phase <input name="nbFirst" type="number" value="2" required/>
	</label>
	"""

	def __init__(self, name, nbMaxPlayers, nbRounds4victory, nbGroups, nbFirst, **_):
		# call the super class constructor
		super().__init__(name, nbMaxPlayers, nbRounds4victory)

		# number of groups
		try:
			self._nbGroups = int(nbGroups)
		except ValueError:
			raise ValueError("The number of groups must be an integer")
		if not 2 <= self._nbGroups <= self.nbMaxPlayers/2:
			raise ValueError("The number of groups must be in 0 and nbMaxPlayer/2")

		# number of players per group that pass the first phase
		try:
			self._nbFirst = int(nbFirst)
		except ValueError:
			raise ValueError("The number of accepted players per group must be an integer")





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

