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

class Championship(Tournament):
	"""
	Championship mode
	"""
	_mode = "Championship"
	_HTMLoptions = ""


	def __init__(self, name, nbMaxPlayers, rounds, **unused):
		# call the super class constructor
		super().__init__(name, nbMaxPlayers, rounds)


	def MatchsGenerator(self):
		"""
		Use the round robin tournament algorithm
		see http://en.wikipedia.org/wiki/Round-robin_tournament and
		http://stackoverflow.com/questions/11245746/league-fixture-generator-in-python/11246261#11246261
		"""
		# copy the player list
		# TODO: vérifier s'ils sont tous encore là ?
		rotation = list(self._players)
		# if player number is odd, we use None as a fake player
		if len(rotation) % 2:
			rotation.append(None)
		# then we iterate using round robin algorithm
		for i in range(0, len(rotation) - 1):
			self._phase = '%d%s phase' % (i+1, 'st' if (i+1) == 1 else 'nd' if (i+1) == 2 else 'rd' if (i+1) == 3 else 'th')
			# generate list of pairs (player1,player2)
			yield list(zip(*[iter(rotation)] * 2))
			# prepare the next list by rotating the list
			rotation = [rotation[0]] + [rotation[-1]] + rotation[1:-1]






class SingleEliminationTournament(Tournament):
	"""
	Single-elimination tournament
	https://en.wikipedia.org/wiki/Single-elimination_tournament
	"""
	_mode = "Single-elimination Tournament"
	_HTMLoptions = """
	<label>
		Nb groups: <input name="nbGroups" type="number" value="4" required/>
	</label>
	<br/>
	<label>
		Nb of players per group that can pass the first phase <input name="nbFirst" type="number" value="2" required/>
	</label>
	"""

	def __init__(self, name, nbMaxPlayers, rounds, nbGroups, nbFirst, **unused):
		# call the super class constructor
		super().__init__(name, nbMaxPlayers, rounds)

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




