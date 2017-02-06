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


from CGS.Tournament import Tournament, numbering
import random
from math import frexp




class PoolKnockout(Tournament):
	mode = "Two stages (pool + knockout) Tournament"
	HTMLoptions = """
	<label>
		Nb groups: <input name="nbGroups" type="number" value="4" required/>
	</label>
	<br/>
	<label>
		Nb of players per group that can pass the first phase:
		<input name="nbFirst" type="radio" value="2" checked required/> 2
	</label>
	"""
	HTMLgameoptions = """
	<label>
		Delay between each move : <input name="delay" type="number" value="0" required/>
	</label>
	"""
	# !TODO: this option should be in Tournament (same option for every tournament)

	def __init__(self, name, nbMaxPlayers, nbRounds4Victory, nbGroups, nbFirst, **_):
		# call the super class constructor
		# (we call it now, because it parses the parameters and we need them)
		# (the drawback is that we need to remove the instance in case of an error here)
		super().__init__(name, nbMaxPlayers, nbRounds4Victory)

		self._score = {}
		self._groups = []
		self._cycle = 0  # 0 during the round robin, 1 during final phase
		self._Draw = []
		# number of groups
		try:
			self._nbGroups = int(nbGroups)
		except ValueError:
			super().removeInstance(name)    # need to remove the instance
			raise ValueError("The number of groups must be an integer")
		if not self._nbMaxPlayers == 0 and not 2 <= self._nbGroups <= self.nbMaxPlayers/2:
			super().removeInstance(name)
			raise ValueError("The number of groups must be in 0 and nbMaxPlayer/2")

		log2nbGroups = frexp(float(nbGroups))[1] - 1  #
		if not 2**log2nbGroups == self._nbGroups:
			super().removeInstance(name)
			raise ValueError("The number of groups should be 2^n")
		# number of players per group that pass the first phase
		try:
			self._nbFirst = int(nbFirst)
		except ValueError:
			super().removeInstance(name)
			raise ValueError("The number of accepted players per group must be an integer")
		if not self._nbMaxPlayers == 0 and not self._nbMaxPlayers//self._nbGroups >= self._nbFirst:
			super().removeInstance(name)
			raise ValueError("There must be enough player in each group to passe the first phase")


	def MatchsGenerator(self):
		"""
		Use the round robin tournament algorithm
		see http://en.wikipedia.org/wiki/Round-robin_tournament and
		http://stackoverflow.com/questions/11245746/league-fixture-generator-in-python/11246261#11246261
		"""
		# score
		self._score = {p: [0, 0, 0] for p in self.players}

		# Put players in groups
		lplayers = list(self._players)
		random.shuffle(lplayers)
		groups = [[] for _ in range(self._nbGroups)]
		g = 0

		while lplayers:
			groups[g].append(lplayers.pop())
			g = (g+1) % self._nbGroups
		self._groups = groups
		nbrounds = []  # nb rounds in each group
		for rotation in groups:
			if len(rotation) % 2:
				rotation.append(None)
			nbrounds.append(len(rotation)-1)
		nmax = max(nbrounds)
		# iterate using round robin algorithm
		for i in range(nmax):
			# update the phase name
			phase = '%d%s round' % (i + 1, numbering(i + 1))
			# list of match by group
			lmatch = []
			for j in range(len(nbrounds)):
				if nbrounds[j] > 0:
					nbrounds[j] -= 1
					rotation = groups[j]
					lmatch += list(zip(*[iter(rotation)] * 2))
					groups[j] = [rotation[0]] + [rotation[-1]] + rotation[1:-1]
			yield phase, lmatch

		# Selection of the best players to be in SingleEliminatioTournament
		# Works only if self._nbFirst == 2
		self._Draw = [[None for _ in range(self._nbFirst * self._nbGroups)]]
		self._cycle = 1  # begin of the final phase
		WinPlayers = []
		for lplayers in self._groups:
			lp = [p for p, score in sorted(self._score.items(),
			                               key=lambda x: str(x[1][0])+str(x[1][1]), reverse=True) if p in lplayers]
			if len(lp) < 2:  # should not happen...
				lp.append(None)
			WinPlayers += lp[:self._nbFirst]

		# Set the players in the draw
		for j in range(self._nbGroups):
			self._Draw[0][2*j] = WinPlayers[2*j]
			self._Draw[0][-2*j-1] = WinPlayers[2*j+1]
		nturn = frexp(self._nbGroups*self._nbFirst)[1]-1  # frexp : log2 int

		for iturn in range(nturn):
			if nturn-iturn > 4:
				phase = '%d%s turn of the final phase' % (iturn + 1, numbering(iturn + 1))
			elif nturn-iturn > 2:
				phase = '1/%d%s final' % (2**(nturn-iturn-1), numbering(2**(nturn-iturn-1)))
			elif nturn-iturn == 2:
				phase = "semi-final"
			else:  # nturn-iturn == 1
				phase = "final"

			yield phase, list(zip(*[iter(self._Draw[-1])] * 2))
			newDraw = []
			Draw = self._Draw[-1]
			for j in range(len(Draw)//2):
				newDraw.append(Draw[2*j] if self._score[Draw[2*j]][2] > self._score[Draw[2*j+1]][2] else Draw[2*j+1])
			self._Draw.append(newDraw)


		# update the winner
		# !!FIXME: set the winner
		self._winner = ""


	def updateScore(self):
		"""
		update the score from the dictionary of games runned in that phase
		Called by runPhase at the end of each phase
		"""
		if self._cycle == 0:
			for (p1, p2), (score, _) in self._games.items():
				self._score[p1][1] += score[0]-score[1]
				self._score[p2][1] += score[1]-score[0]
				if score[0] > score[1]:
					self._score[p1][0] += 1
				else:
					self._score[p2][0] += 1
		elif self._cycle == 1:
			for (p1, p2), (score, _) in self._games.items():
				if score[0] > score[1]:
					self._score[p1][2] = 1
					self._score[p2][2] = 0
				else:
					self._score[p1][2] = 0
					self._score[p2][2] = 1


	def HTMLscore(self):
		"""
		Display the actual score

		Returns a HTML string
		"""

		HTMLs = ""

		if self._cycle == 1:

			for t in self._Draw[::-1]:
				HTMLs += "".join("%s %d-- %s %d<br>" % (t[2*i].HTMLrepr(), self._score[t[2*i]][2], t[2*i+1].HTMLrepr(),
				                                        self._score[t[2*i+1]][2]) for i in range(len(t)//2))
				HTMLs += "<br>"

		if self._score and self._groups:
			for i, lplayers in enumerate(self._groups):
				HTMLs += "Pool "+str(i+1)+"<br/>"
				# note : the key of sorting is str to have a lexicographic ordering
				HTMLs += "<ul>" + "".join(
					"<li>%s: %d(%+d) points</li>" % (p.HTMLrepr(), score[0], score[1])
					for p, score in sorted(self._score.items(), key=lambda x: str(x[1][0])+str(x[1][1]), reverse=True)
					if p in lplayers) + "</ul>"


			# return "<ul>" + "".join(
			# "<li>%s: %d points</li>" % (p.HTMLrepr(), score) for p, score in self._score.items()) + "</ul>"

		return HTMLs

