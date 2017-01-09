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


# TODO: Tournament class should be virtual (abstract)

class Tournament:
	"""
	Class for the tournament
	only subclasses should be used directly
	Subclasses object can be created using Tournament.factory(...)

	Attributes:
		- _name: (string) name of the tournament
		- _nbMaxPlayer: (int) maximum number of players (0 for unlimited)
		- _rounds: (int) number of rounds (usually 2 or 3)
		- _players: (list of Players) list of engaged players
		- _isRunning: (bool) True if the tournament is running (False if it'is still waiting for players)
		- _games: dictionnary of current games
		- _phase: (string) name of the phase ('not running', '1/4 final', etc...)

	Class attributes
		- _HTMLoptions: (string) HTML code to display the options in a form
		- _mode: (string) mode of the tournament (like 'championship' or 'single-elimination Tournament')
		        the short name is given by the class name
		- allTournaments: dictionary of all the existing tournament (name->tournament)

	"""

	allTournaments = {}         # dictionary of all the tournament
	_HTMLoptions = ""           # some options to display in an HTML form
	_mode = ""        # type of the tournament

	def __init__(self, name, nbMaxPlayers, rounds):
		"""
		Create a Tournament

		Should not be directly (only used by the __init__ of the subclasses)

		Parameters:
		- name: (string) name of the tournament (used for the
		- nbMaxPlayers: (integer) number maximum of players in the tournament (0 for no limit)
		- rounds: (integer) number of rounds for 2 opponent (1 to 3)
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

		# get nb of rounds
		try:
			self._rounds = int(rounds)
		except ValueError:
			raise ValueError("The number of rounds is not valid")

		self._players = []  # list of engaged players
		self._isRunning = False     # is the tournament already running ?
		self._games = {}        		# list of current games

		# TODO: add a logger

		# and last, add itself to the dictionary of tournaments
		if name in self.allTournaments:
			raise ValueError("A tournament with the same name already exist")
		self.allTournaments[name] = self



	@property
	def name(self):
		return self._name

	@property
	def mode(self):
		return self._mode

	@property
	def nbMaxPlayers(self):
		return self._nbMaxPlayers

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
		if tournamentName not in cls.allTournaments:
			raise ValueError("The tournament '%s' doesn't not exist" % tournamentName)
		t = cls.allTournaments[tournamentName]

		# check if the tournament is open
		if t.isRunning and player not in t.players: # TODO tester  2nd tour...
			# TODO: log it in t.logger
			raise ValueError("The tournament '%s' is now closed." % tournamentName)

		# add the player to the tournament
		# TODO: 2nd tour à gérer
		if t.nbMaxPlayers == 0 or len(t.players) < t.nbMaxPlayers:
			t.players.append(player)
		# TODO: log it (in player.logger and self.logger)
		else:
			raise ValueError("The tournament '%s' already has its maximum number of players" % t.name)


	@classmethod
	def getFromName(cls, name):
		"""
		Get a tournament form its name
		Parameters:
		- name: (string) name of the tournament

		Returns the tournament (the object) or None if it doesn't exist
		"""
		return cls.allTournaments.get(name, None)


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
		modes = "\n".join("<option value='%s'>%s</option>" % (sc.__name__, sc._mode) for sc in cls.__subclasses__())

		# HTMLmodeOptions
		options = "\n".join('<div display="none" id="%s">%s</div>' %
		                    (sc.__name__, sc._HTMLoptions) for sc in cls.__subclasses__())

		# JavascriptModeOptions
		jOptions = "\n".join('document.getElementById("%s").style.display="none";' %
		                     (sc.__name__,) for sc in cls.__subclasses__())

		return {"HTMLmodes": modes, "HTMLmodeOptions": options, "JavascriptModeOptions": jOptions}





	def runPhase(self):
		"""Launch a phase of the tournament
		"""
		self._isRunning = True
		# get the next list of 2-tuple (player1,player2) of players who will player together in that phase
		matches = next(self.MatchsGenerator())
		# build the dictionary of the games (pair of players -> list of score (tuple) and current game
		self._games = {(p1, p2): [(0, 0), None] for p1, p2 in matches if p1 and p2}
		# run the games
		for r in range(self.rounds):
			for p1, p2 in self._games.keys():
				# TODO: should we check that the two players are still here ????
				if self.rounds == r and self.rounds % 2 == 1:
					if self._games[(p1,p2)][0][0] == self._games[(p1,p2)][0][1]:
						# we have equality in score, so we need another game
						# TODO: vérifier que ça marche (qd on a égalité ou pas pour le dernier tour)
						self._games[(p1, p2)][1] = Game(p1, p2)
				else:
					self._games[(p1, p2)][1] = Game(p1, p2, start=(r-1) % 2)



	def MatchsGenerator(self):
		"""
		TO BE OVERLOADED
		"""
		yield [None, None]