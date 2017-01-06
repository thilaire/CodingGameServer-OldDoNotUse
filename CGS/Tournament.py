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

"""

from re import sub
from CGS.TournamentMode import TournamentMode
from CGS.Game import Game

class Tournament:

	allTournaments = {}        # dictionary of all the tournament

	def __init__(self, name, nbMaxPlayers, rounds, mode):
		"""
		Create a Tournament
		Parameters:
		- name: (string) name of the tournament (used for the
		- nbMaxPlayers: (integer) number maximum of players in the tournament (0 for no limit)
		- rounds: (integer) number of rounds for 2 opponent (1 to 3)
		- mode: (string) name of the tournament mode ("championship", etc.)
		"""
		# name of the tournament
		self._name = sub('\W+', '', name)
		# check if the name is valid (20 characters max, and only in [a-zA-Z0-9_]
		if name != self._name or len(name) > 20:
			raise ValueError("The name of the tournament is not valid (must be 20 characters max, and only in [a-zA-Z0-9_]")

		# maximum number of players
		try:
			self._nbMaxPlayers = int(nbMaxPlayers)
		except ValueError:
			raise ValueError("The nb maximum of players is not valid")
		if self._nbMaxPlayers < 0:
			raise ValueError("The nb maximum of players should be positive")

		self._players = []          # list of engaged players
		self._rounds = rounds       # nb of rounds

		self._isRunning = False

		# tournament mode (championship, single-elimination, etc.)
		self._mode = TournamentMode.getFromName(mode)(self._players)
		if self._mode is None:
			raise ValueError("The mode is incorrect, should be in")


		# TODO: check the number of rounds

		# add itself to the dictionary of tournaments
		if name in self.allTournaments:
			raise ValueError("A tournament with the same name already exist")
		self.allTournaments[name] = self

		# TODO: add a logger


	@property
	def name(self):
		return self._name

	@property
	def nbMaxPlayers(self):
		return self._nbMaxPlayers

	@property
	def mode(self):
		return self._mode.name

	@property
	def rounds(self):
		return self._rounds

	@property
	def players(self):
		return self._players

	@property
	def isRunning(self):
		return self._isRunning

	def HTMLrepr(self):
		return "<B><A href='/tournament/%s'>%s</A></B>" % (self.name, self.name)



	def addPlayer(self, player):
		"""
		Add a player in that tournament
		Parameter:
		- player: (Player) player to be added in the tournament
		"""
		if self._isRunning:
			raise ValueError("The tournament '%s' is already running" % self.name)
		if self._nbMaxPlayers == 0 or len(self._players) < self._nbMaxPlayers:
			self._players.append(player)
			# TODO: log it (in player.logger and self.logger)
		else:
			raise ValueError("The tournament '%s' already has its maximum number of players" % self.name)




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
		if tournamentName not in cls.allTournaments:
			raise ValueError("The tournament '%s' doesn't not exist" % tournamentName)
		t = cls.allTournaments[tournamentName]

		# check if the tournament is open
		if not t.isOpen:
			# TODO: log it in t.logger
			raise ValueError("The tournament '%s' is now closed." % tournamentName)

		# add the player to the tournament
		t.addPlayer(player)


	@classmethod
	def getFromName(cls, name):
		"""
		Get a tournament form its name
		Parameters:
		- name: (string) name of the tournament

		Returns the tournament (the object) or None if it doesn't exist
		"""
		return cls.allTournaments.get(name, None)

	def runPhase(self):
		"""Launch a phase of the tournament
		"""
		self._isRunning = True
		# get the list of 2-tuple (player1,player2) of players who will player together in that phase
		matches = self.mode.getPlayersForNextPhase()
		# run the games
		for round in self.rounds:
			for p1,p2 in matches:
				if round==3 or self.rounds==1:
					self._games.append(Game(p1,p2))         # random God choose who starts
				else:
					self._games.append(Game(p1,p2,start=round-1))
