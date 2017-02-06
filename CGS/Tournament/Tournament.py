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


# !!TODO: add some other options in the HTML form (timeout, possibility to run all the phases without stop, etc.)
# !!TODO: remove unnecessary properties (used once in the HTML when it was not dynamic)


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
		- _players: dictionary (name: player) of engaged players (None if the player has left)
		- _games: dictionnary of current games (pName1, pName2) -> [score,Game]
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
	# !TODO: clarify (may be just change the name) the difference betwwen HTMLoptions and HTMLgameoptions
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

		self._players = {}              # dictionary (name: player) of engaged players
		self._games = {}        		# list of current games
		self._queue = Queue()           # queue only used for join method, to wait for all the tasks to be done
		self._matches = []              # list of current (or next) matches in the phase
		self._state = 0                 # current state
		self._phase = ""                # name of the phase
		self._round = 0
		self._winner = ""               # name of the winner

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
		self.logger.message("The tournament is now over: %s wins !!", self._winner)
		self._state = 3
		Tournament.removeInstance(self.name)
		# !!TODO: disconnect all the players of that tournament ?

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
			return "Tournament over: %s is the winner" % self._winner


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
			if player.name not in t.players:
				t.logger.info("Player %s wanted to enter, but the tournament has began.", player.name)
				raise ValueError("The tournament '%s' has already began." % tournamentName)
			else:
				# check if the player is fully registred or has already disconnected
				if not t.players[player.name]:
					# previously disconnected player
					t.logger.info("Player `%s` is back in the tournament", player.name)
					t.players[player.name] = player
					player.tournament = t
					# update the sockets
					t.sendUpdateToWebSocket()
				else:
					# ok, nothing to do, the player is already registred
					pass
		else:
			if t.nbMaxPlayers == 0 or len(t.players) < t.nbMaxPlayers:
				# add the player in the players dictionary
				t.logger.info("Player `%s` has joined the tournament", player.name)
				t.players[player.name] = player
				player.tournament = t
				# update the sockets
				t.sendUpdateToWebSocket()
			else:
				t.logger.info("Player `%s` wanted to enter, but the tournament already has its maximum number of players.",
				              player.name)
				player.logger.info("Impossible to enter the tournament `%s`, it already has its maximum number of players",
				                   t.name)
				raise ValueError("The tournament `%s` already has its maximum number of players" % t.name)


	def unregisterPlayer(self, playerName):
		"""
		Called by PlayerSocket when the player disconnects
		The player's name is kept in the dictionary, but with no player associated (with None instead)
		:param playerName: (string) name of the player who disconnects
		:return:
		"""
		# check if the player is in that tournament
		if playerName not in self._players:
			raise ValueError("The player is not register in the tournament %s" % self.name)
		# remove that player
		self._players[playerName] = None
		self.logger.info("Player `%s` has quit the tournament", playerName)
		# update the sockets
		self.sendUpdateToWebSocket()


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


	def playerHTMLrepr(self, playerName):
		"""
		Get the HTML representation of a player from its name
		Check if the player is still connected or not
		:param playerName: (string) name of the player
		:return: (string) HTML representation
		"""
		p = self._players[playerName]
		return p.HTMLrepr() if p else playerName



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
		if (winner.name, looser.name) in self._games:
			score = self._games[(winner.name, looser.name)][0]
			score[0] += 1
			self._games[(winner.name, looser.name)][1] = None
		else:
			score = self._games[(looser.name, winner.name)][0]
			score[1] += 1
			self._games[(looser.name, winner.name)][1] = None
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

		# first launch ?
		if not self.hasBegan:
			# we first need to get the list of 2-tuple (player1's name, player2's name)
			# of players who will play together in the phase
			try:
				phase, self._matches = next(self._matchGen)
			except StopIteration:
				self.endTournament()
			else:
				self.newPhase(phase)
		else:
			# otherwise, start a new phase
			self.newPhase()

		# build the dictionary of the games (pair of players' name -> list of score (tuple) and current game
		# (we remove fake players with "" as name)
		self._games = {(pName1, pName2): [[0, 0], None] for pName1, pName2 in self._matches if pName1 and pName2}
		# run the games
		for self._round in range(1, self.nbRounds4Victory + 1):

			for (pName1, pName2), (score, _) in self._games.items():

				if max(score) < self.nbRounds4Victory:
					# choose who starts (-1 for random)
					start = (self._round-1) % 2 if self._round < self.nbRounds4Victory else -1

					# run the game only if the two players are here (otherwise, one wins directly)
					player1, player2 = self._players[pName1], self._players[pName2]
					if player1 and player2:

						self._games[(pName1, pName2)][1] = Game.getTheGameClass()(
								player1, player2, start=start, tournament=self, **kwargs)
						self.logger.info("The game `%s` vs `%s` starts", pName1, pName2)
						self._queue.put_nowait(None)
					else:
						# one player is not playing anymore (disconnected), so the other wins
						score = self._games[(pName1, pName2)][0]
						if player1 is not None:
							score[0] += 1
						elif player2 is not None:
							score[1] += 1
						else:
							# in the case where the 2 players are disconnected, the 1st win...
							# !FIXME: introduce equality (the result of a game is either WIN, LOOSE or EQUALITY !)
							score[start] += 1

			# update the websockets (no need to update everytime a game is added)
			self.sendUpdateToWebSocket()
			# and wait for all the games to end (before running the next round)
			self._queue.join()
			time.sleep(1)       # !!TODO: check why is not fully working when we remove this sleep....

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
		# build the list of games HTML representation
		listGames = []
		if self.isPhaseRunning:
			# build the HTML representation for the running games
			for (p1, p2), (score, game) in self._games.items():
				HTMLp1 = self.playerHTMLrepr(p1)
				HTMLp2 = self.playerHTMLrepr(p2)
				if game:
					listGames.append("%s %s %s (%s)" % (HTMLp1, score, HTMLp2, game.HTMLrepr()))
				else:
					listGames.append("%s %s %s" % (HTMLp1, score, HTMLp2))
		else:
			# build the HTML representation for the next games
			for p1, p2 in self._matches:
				if p1 and p2:
					HTMLp1 = self.playerHTMLrepr(p1)
					HTMLp2 = self.playerHTMLrepr(p2)
					listGames.append("%s vs %s" % (HTMLp1, HTMLp2))

		# build the list of players HTML representation
		listPlayers = [self.playerHTMLrepr(name) for name in self._players.keys()]

		# return the dictionary used by the websocket
		return {'nbPlayers': len(self._players), 'Players': listPlayers,
		        'HTMLbutton': self.HTMLButton(),
		        'phase': self.getStatus(), 'Games': listGames,
		        'score': self.HTMLscore(),
		        'next_games': 'Games' if self.isPhaseRunning else 'Next games'}




	def MatchsGenerator(self):
		"""
		TO BE OVERLOADED
		"""
		yield "", [("", "")]


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

