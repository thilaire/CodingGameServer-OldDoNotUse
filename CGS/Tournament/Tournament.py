"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev...

File: Tournament.py
	Contains the class Tournament
	-> defines the generic Tournament's behavior
	-> should not be used directly to build a Tournament object (its subclasses are used)

"""

import time     # do not import sleep from time (but rather use time.sleep()) because of the gevent's monkeypatch
from queue import Queue
from re import sub

from CGS.Game import Game
from CGS.BaseClass import BaseClass


def numbering(i):
	"""Returns the 2-letter string associated to a number
	1->st
	2->nd
	3->rd
	others->th
	(a dictionary may be used, instead)
	"""
	if i == 1:
		return 'st'
	elif i == 2:
		return 'nd'
	elif i == 3:
		return 'rd'
	else:
		return 'th'


# TODO: Tournament class should be virtual (abstract)
class Tournament(BaseClass):
	"""
	Class for the tournament
	only subclasses should be used directly
	Subclasses object can be created using Tournament.factory(...)

	Attributes:
		- _name: (string) name of the tournament
		- _nbMaxPlayer: (int) maximum number of players (0 for unlimited)
		- _nbRounds4Victory: (int) number of rounds  for a victory (usually 1 or 2)
		- _players: (list of Players) list of engaged players
		- _games: dictionnary of current games
		- _queue: (Queue) queue of running game (used to wait for all the games to be ended)
		- _state: (int) intern state of the tournament
			0 -> not yet began
			1 -> a phase is running
			2 -> wait for a new phase
			3 -> end of the tournament
		- _phase: (string) name of the current (or next) phase
		- _round: (int) actual round

	Class attributes
		- _HTMLoptions: (string) HTML code to display the options in a form
		- _mode: (string) mode of the tournament (like 'championship' or 'single-elimination Tournament')
		        the short name is given by the class name
		- allTournaments: dictionary of all the existing tournament (name->tournament)

	"""
	allInstances = {}         # dictionary of all the tournaments
	HTMLoptions = ""          # some options to display in an HTML form
	HTMLgameoptions = ""       # some options to display game options in an HTML form
	# TODO: clarify (may be just change the name) the difference betwwen HTMLoptions and HTMLgameoptions
	mode = ""               # type of the tournament

	def __init__(self, name, nbMaxPlayers, nbRounds4Victory):
		"""
		Create a Tournament

		Should not be directly (only used by the __init__ of the subclasses)

		Parameters:
		- name: (string) name of the tournament (used for the
		- nbMaxPlayers: (integer) number maximum of players in the tournament (0 for no limit)
		- maxVictories: (integer) maximum number of victories to win the match (1, 2 or 3): 1 means the 1st player is randomly determined
		"""
		# name of the tournament
		self._name = sub('\W+', '', name)
		# check if the name is valid (20 characters max, and only in [a-zA-Z0-9_]
		if name != self._name or len(name) > 20:
			raise ValueError("The name of the tournament is not valid (must be 20 characters max, and only in [a-zA-Z0-9_]")

		# get maximum number of players
		try:
			self._nbMaxPlayers = int(nbMaxPlayers)
		except ValueError:
			raise ValueError("The nb maximum of players is not valid")
		if self._nbMaxPlayers < 0:
			raise ValueError("The nb maximum of players should be positive")

		# get maximum number of games for a victory (gives the nb of rounds)
		try:
			self._nbRounds4Victory = int(nbRounds4Victory)
		except ValueError:
			raise ValueError("The number of needed rounds for a victory is not valid")

		self._players = []  # list of engaged players
		self._games = {}        		# list of current games
		self._queue = Queue()           # queue only used for join method, to wait for all the tasks to be done
		self._matches = []              # list of current (or next) matches in the phase
		self._state = 0                 # current state
		self._phase = ""                # name of the phase
		self._round = 0

		# match generator
		self._matchGen = self.MatchsGenerator()

		# and last, call the constructor of BaseClass
		super().__init__(name)
		# and log it
		self._logger.message("=======================")
		self._logger.message("The tournament %s is now created (%s)", name, self.__class__.__name__)


	@property
	def name(self):
		return self._name

	@property
	def nbMaxPlayers(self):
		return self._nbMaxPlayers

	@property
	def nbRounds4Victory(self):
		return self._nbRounds4Victory

	@property
	def players(self):
		return self._players


	def HTMLrepr(self):
		return "<B><A href='/tournament/%s'>%s</A></B>" % (self.name, self.name)

	@property
	def games(self):
		return self._games

	@property
	def hasBegan(self):
		"""Returns True if the tournament has already began"""
		return self._state != 0

	@property
	def isFinished(self):
		"""Returns True if the tournament is finished"""
		return self._state == 3

	@property
	def isPhaseRunning(self):
		"""Returns True if a phase is running"""
		return self._state == 1

	def newPhase(self, phase=None):
		"""Call to indicates a new phase
		Parameter:
		- phase: (string) name of the new phase
		"""
		self._state = 1
		if phase:
			self._phase = phase
		# log it
		self.logger.message("The phase `%s` now starts", self._phase)

	def endPhase(self, newPhase):
		"""Called to indicate the end of the phase (so we wait for a new phase)"""
		self.logger.message("The phase `%s` ends", self._phase)
		self._state = 2
		self._phase = newPhase


	def endTournament(self):
		"""Called to indicate the end of the tournament"""
		self.logger.message("The tournament is now over !")
		# TODO: log the winner (need to add a new attribute, that the child class should set at the end of the tournament)
		self._state = 3
		Tournament.removeInstance(self.name)

	@property
	def phase(self):
		"""Returns the name of the current (or next) phase"""
		return self._phase

	def HTMLButton(self):
		"""
		Returns the HTML code for the "next" button
		-> may be enable or disable, with a label depending on the state
		"""
		HTMLstr = "<input type='button' name='send' id='nextPhaseButton' %s value='%s'></input>"
		if self._state == 0:
			# "run Tournament" button
			return HTMLstr % ('', 'Run Tournament !!')
		elif self._state == 1:
			# disabled "next Phase" button
			return HTMLstr % ('disabled', 'Next Phase (%s)' % self._phase)
		elif self._state == 2:
			# enable "next Phase" button
			return HTMLstr % ('', 'Next Phase (%s)' % self._phase)
		else:
			# no button anymore
			return ""

	def getStatus(self):
		"""
		Returns a string describing the status (about the current phase or the next phase)
		"""
		if self._state == 0:
			return "Ready to start !"
		elif self._state == 1:
			return "Running phase: %s (%d%s round)" % (self._phase, self._round, numbering(self._round))
		elif self._state == 2:
			return "Next phase: " + self._phase
		else:
			return "Tournament over"


	@classmethod
	def factory(cls, mode, **options):
		"""Create a tournament from a mode and some values (should include name, nbMaxPlayers, rounds)
		Parameters:
			- mode: (string) should be one of the subclasses name
		"""
		# dictionary of all the subclasses (championship, single-elimination, etc.)
		d = {sc.__name__: sc for sc in cls.__subclasses__()}
		if mode in d:
			return d[mode](**options)
		else:
			# pretty print the subclasses list
			keys = ["'"+x+"'" for x in d.keys()]
			if len(keys) > 1:
				modes = " or ".join([", ".join(keys[:-1]), keys[-1]])
			else:
				modes = keys[0]
			raise ValueError("The mode is incorrect, should be " + modes)


	@classmethod
	def registerPlayer(cls, player, tournamentName):
		"""
		Register a player into a tournament, from its name
		(register if its exists and is opened)
		Parameters:
		- player: (Player) player that want to register into a tournament
		- tournamentName: (string) name of the tournament
		"""
		# check if the tournament exists
		if tournamentName not in cls.allInstances:
			raise ValueError("The tournament '%s' doesn't not exist" % tournamentName)
		t = cls.allInstances[tournamentName]

		# check if the tournament is open
		if t.hasBegan:
			if player not in t.players:
				t.logger.info("Player %s wanted to enter, but the tournament has began.", player.name)
				raise ValueError("The tournament '%s' has already began." % tournamentName)
			else:
				# ok, nothing to do, the player is already registred
				pass
		else:
			if t.nbMaxPlayers == 0 or len(t.players) < t.nbMaxPlayers:
				# add the player in the players list
				t.players.append(player)
				t.logger.info("Player `%s` has joined the tournament", player.name)
				player.logger.info("We have entered the tournament `%s`", t.name)
				# update the sockets
				t.sendUpdateToWebSocket()
			else:
				t.logger.info("Player `%s` wanted to enter, but the tournament already has its maximum number of players.",
				              player.name)
				player.logger.info("Impossible to enter the tournament `%s`, it already has its maximum number of players",
				                   t.name)
				raise ValueError("The tournament `%s` already has its maximum number of players" % t.name)



	@classmethod
	def HTMLFormDict(cls):
		"""
		Returns a dictionary to fill the template new_tournament.html
		It's about all the existing types of tournament (subclasses of Tournament class)

		The dictionary contains:
		- "HTMLmode": an HTML string, containing a <SELEC> element to be included in HTML file
			It's a drop-down list with all the existing modes
		- "HTMLmodeOptions": an HTML string, containing a <div> per mode; each div contains the HTML form for its own options
		"""
		# HTMLmode
		modes = "\n".join("<option value='%s'>%s</option>" % (sc.__name__, sc.mode) for sc in cls.__subclasses__())

		# HTMLmodeOptions
		options = "\n".join('<div display="none" id="%s">%s</div>' %
		                    (sc.__name__, sc.HTMLoptions) for sc in cls.__subclasses__())

		# JavascriptModeOptions
		jOptions = "\n".join('document.getElementById("%s").style.display="none";' %
		                     (sc.__name__,) for sc in cls.__subclasses__())

		return {"HTMLmodes": modes, "HTMLmodeOptions": options, "JavascriptModeOptions": jOptions}


	def HTMLlistOfGames(self):
		"""
		Returns a HTML string to display the list of games
		It displays informations from the dictionary _games
		"""
		HTMLgames = []
		for (p1, p2), (score, g) in self._games.items():       # unpack all the games of the phase
			if g:
				HTMLgames.append("%s (%d) vs (%d) %s (%s)" % (p1.HTMLrepr(), score[0], score[1], p2.HTMLrepr(), g.HTMLrepr()))
			else:
				HTMLgames.append("%s (%d) vs (%d) %s" % (p1.HTMLrepr(), score[0], score[1], p2.HTMLrepr()))

		return "<br/>".join(HTMLgames)


	def endOfGame(self, winner, looser):
		"""
		Called when a game finished.
		Change the dictionary _games accordingly (increase the score, remove the game, etc.)
		Parameters:
		- winner: (Player) player who wins the game
		- looser: (Player) player who loose the game
		"""
		# log it
		self.logger.info("`%s` won its game against `%s`", winner.name, looser.name)
		# modify the score in the dictionary
		if (winner, looser) in self._games:
			score = self._games[(winner, looser)][0]
			score[0] += 1
			self._games[(winner, looser)][1] = None
		else:
			score = self._games[(looser, winner)][0]
			score[1] += 1
			self._games[(looser, winner)][1] = None
		# remove one item from the queue
		self._queue.get()
		self._queue.task_done()
		self.sendUpdateToWebSocket()



	def runPhase(self, **kwargs):
		"""Launch a phase of the tournament
		"""
		# check if a phase is not already running
		if self.isPhaseRunning:
			# do noting, since a phase is already running
			return

		# first launch
		if not self.hasBegan:
			# we first need to get the list of 2-tuple (player1,player2) of players who will play together in the phase
			try:
				phase, self._matches = next(self._matchGen)
			except StopIteration:
				self.endTournament()
			else:
				self.newPhase(phase)
		else:
			self.newPhase()

		# build the dictionary of the games (pair of players -> list of score (tuple) and current game
		# TODO: rename _games variable: it's more than a simple match (several rounds)
		self._games = {(p1, p2): [[0, 0], None] for p1, p2 in self._matches if p1 and p2}
		# run the games
		for self._round in range(1, self.nbRounds4Victory + 1):

			for (p1, p2), (score, _) in self._games.items():

				if max(score) < self.nbRounds4Victory:
					# choose who starts (-1 for random)
					start = (self._round-1) % 2 if self._round < self.nbRounds4Victory else -1
					# TODO : pass the TIMEOUT parameter
					self._games[(p1, p2)][1] = Game.getTheGameClass()(p1, p2, start=start, tournament=self, **kwargs)
					self.logger.info("The game `%s` vs `%s` starts", p1.name, p2.name)
					self._queue.put_nowait(None)

			# update the websockets (no need to update everytime a game is added)
			self.sendUpdateToWebSocket()
			# and wait for all the games to end (before running the next round)
			self._queue.join()
			time.sleep(1)       # TODO: check why is not fully working when we remove this sleep....

		# update the scores
		self.updateScore()

		# Prepare the next list of 2-tuple (player1,player2) of players who will play in next phase
		try:
			phase, self._matches = next(self._matchGen)
		except StopIteration:
			# no more matches to run (end of the tournament)
			self.endTournament()
		else:
			self.endPhase(phase)

		# update data through websockets
		self.sendUpdateToWebSocket()


	def getDictInformations(self):
		"""

		:return:
		"""
		listGames = []

		if self.isPhaseRunning:
			# build the HTML representation for the running games
			for (p1, p2), (score, game) in self._games.items():
				if game:
					listGames.append("%s: %s %s %s" % (game.HTMLrepr(), p1.HTMLrepr(), score, p2.HTMLrepr()))
		else:
			# build the HTML representation for the next games
			for p1, p2 in self._matches:
				if p1 and p2:
					listGames.append("%s vs %s" % (p1.HTMLrepr(), p2.HTMLrepr()))

		# return the dictionary used by the websocket
		return {'nbPlayers': len(self._players), 'Players': [p.HTMLrepr() for p in self._players],
		        'HTMLbutton': self.HTMLButton(),
		        'phase': self.getStatus(), 'Games': listGames,
		        'score': self.HTMLscore(),
		        'next_games': 'Games' if self.isPhaseRunning else 'Next games'}




	def MatchsGenerator(self):
		"""
		TO BE OVERLOADED
		"""
		yield [None, None]


	def HTMLscore(self):
		"""
		Display the actual score

		TO BE OVERLOADED

		Returns a HTML string to display the score
		"""
		return ""

	def updateScore(self):
		"""
		update the score from the dictionary of games runned in that phase
		Called by runPhase at the end of each phase

		TO BE OVERLOADED

		"""
		pass

