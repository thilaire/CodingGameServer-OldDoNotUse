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

from re import sub
from CGS.Game import Game
from queue import Queue
from CGS.WebSocketBase import WebSocketBase

import time


# TODO: Tournament class should be virtual (abstract)


class Tournament(WebSocketBase):
	"""
	Class for the tournament
	only subclasses should be used directly
	Subclasses object can be created using Tournament.factory(...)

	Attributes:
		- _name: (string) name of the tournament
		- _nbMaxPlayer: (int) maximum number of players (0 for unlimited)
		- _nbRounds4Victory: (int) number of rounds  for a victory (usually 1 or 2)
		- _players: (list of Players) list of engaged players
		- _isRunning: (bool) True if the tournament is running (False if it'is still waiting for players)
		- _games: dictionnary of current games
		- _phase: (string) name of the phase ('not running', '1/4 final', etc...)
		- _isRunningPhase: (bool) True if a phase is running (false when we wait the user to run a new phase)
		- _queue: (Queue) queue of running game (used to wait for all the games to be ended)

	Class attributes
		- _HTMLoptions: (string) HTML code to display the options in a form
		- _mode: (string) mode of the tournament (like 'championship' or 'single-elimination Tournament')
		        the short name is given by the class name
		- allTournaments: dictionary of all the existing tournament (name->tournament)

	"""
	allInstances = {}         # dictionary of all the tournaments
	HTMLoptions = ""           # some options to display in an HTML form
	mode = ""        # type of the tournament

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
		self._isRunning = False         # is the tournament already running ?
		self._isPhaseRunning = False    # is there is a running phase
		self._games = {}        		# list of current games
		self._queue = Queue()   # we use a queue, even we do not need to store item inside (just need the .join method to wait for all the task been done)
		self._phase = ""                # phase of the tournament


		# match generator
		self._matchGen = self.MatchsGenerator()

		# TODO: add a logger

		# and last, call the constructor of WebSocketBase
		if name in self.allInstances:
			raise ValueError("A tournament with the same name already exist")
		super().__init__(name)



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

	@property
	def isRunning(self):
		return self._isRunning

	@property
	def isPhaseRunning(self):
		return self._isPhaseRunning

	def HTMLrepr(self):
		return "<B><A href='/tournament/%s'>%s</A></B>" % (self.name, self.name)

	@property
	def games(self):
		return self._games

	@property
	def phase(self):
		return self._phase


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
		if t.isRunning:
			if player not in t.players:
				# TODO: log it in t.logger
				raise ValueError("The tournament '%s' is now closed." % tournamentName)
			else:
				# ok, nothing to do, the player is already registred
				pass
		else:
			# TODO: log it (in player.logger and self.logger)
			if t.nbMaxPlayers == 0 or len(t.players) < t.nbMaxPlayers:
				t.players.append(player)
				t.sendUpdateToWebSocket()
			else:
				raise ValueError("The tournament '%s' already has its maximum number of players" % t.name)



	@classmethod
	def HTMLFormDict(cls):
		"""
		Returns a dictionary to fill the template new_tournament.html
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



	def runPhase(self):
		"""Launch a phase of the tournament
		"""
		# check if a phase is not already running
		if self._isPhaseRunning:
			return
		self._isRunning = True
		self._isPhaseRunning = True

		# get the next list of 2-tuple (player1,player2) of players who will player together in that phase
		try:
			matches = next(self._matchGen)
		except StopIteration:
			# no more matches to run (end of the tournament)
			self._isRunning = False
			self._isPhaseRunning = False
			return

		# build the dictionary of the games (pair of players -> list of score (tuple) and current game
		# TODO: rename _games variable: c'est plus qu'un simple match, vu qu'il y a la revanche (plusieurs tours)
		self._games = {(p1, p2): [[0, 0], None] for p1, p2 in matches if p1 and p2}

		# run the games
		for r in range(1, self.nbRounds4Victory + 1):

			for (p1, p2), (score, _) in self._games.items():

				if max(score) < self.nbRounds4Victory:
					# choose who starts (-1 for random)
					start = (r-1) % 2 if r < self.nbRounds4Victory else -1
					self._games[(p1, p2)][1] = Game.getTheGameClass()(p1, p2, start=start, tournament=self)
					self._queue.put_nowait(None)

			# update the websockets (no need to update everytime a game is added)
			self.sendUpdateToWebSocket()
			# and wait for all the games to end (before running the next round)
			self._queue.join()
			time.sleep(1)       # TODO: check why is not fully working when we remove this sleep....


		# update the scores
		self.updateScore()

		# end of the phase, we are ready to run another one
		self._isPhaseRunning = False
		self.sendUpdateToWebSocket()


	def getDictInformations(self):
		"""

		:return:
		"""
		# build the HTML representation for the running games
		listGames = []
		for (p1, p2), (score, game) in self._games.items():
			if game:
				listGames.append("%s: %s %s %s" % (game.HTMLrepr(), p1.HTMLrepr(), score, p2.HTMLrepr()))
		# return the dictionary used by the websocket
		return {'nbPlayers': len(self._players), 'Players': [p.HTMLrepr() for p in self._players],
		        'runPhaseButton': not self._isPhaseRunning,
		        'phase': self._phase, 'Games': listGames,
		        'score': self.HTMLscore()}




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

