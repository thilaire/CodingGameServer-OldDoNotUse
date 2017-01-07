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
	Contains the class TournamentMode
	-> defines the different tournaments behavior

"""


# TODO: faut-il fusionner les deux classes TournamentMode et Tournament en une seule
# enfin, faire de Championship et SingleEliminationTournament des sous-classes de Tournament, tout simplement ????
# ou bien est-ce le découpage est satisfaisant (clair ??)


class TournamentMode:
	# to be overloaded
	_name = ""
	_HTMLoptions = ""

	def __init__(self, players):
		"""
		Construct a TournamentMode
		:param players:
		"""
		self._players = players     # list of playes who will participate (get the reference of the list of players)
		self._phase = "not running"


	@property       # WARNING: property de class !!! (enlever?)
	def name(self):
		return self._name

	@property
	def HTMLoptions(self):
		return self._HTMLoptions

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
		modes = "\n".join("<option value='%s'>%s</option>" % (sc.__name__, sc._name) for sc in cls.__subclasses__())

		# HTMLmodeOptions
		options = "\n".join('<div display="none" id="%s">%s</div>' %
		                    (sc.__name__, sc._HTMLoptions) for sc in cls.__subclasses__())

		# JavascriptModeOptions
		jOptions = "\n".join('document.getElementById("%s").style.display="none";' %
		                     (sc.__name__,) for sc in cls.__subclasses__())

		return {"HTMLmodes": modes, "HTMLmodeOptions": options, "JavascriptModeOptions": jOptions}



	@classmethod
	def getFromName(cls, name):
		"""
		Get a tournament mode from its name (name of the class)
		Parameter:
		- name: (string) name of the mode we want to get
		Returns the Tournament mode, or None if it doesn't exist
		"""
		d = {sc.__name__: sc for sc in cls.__subclasses__()}
		return d.get(name, None)


	# to be overloaded
	def MatchsGenerator(self):
		pass



class Championship(TournamentMode):
	"""
	Championship mode
	"""
	_name = "Championship"
	_HTMLoptions = ""

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
			# generate list of pairs (player1,player2)
			yield zip(*[iter(rotation)] * 2)
			# prepare the next list by rotating the list
			rotation = [rotation[0]] + [rotation[-1]] + rotation[1:-1]


class SingleEliminationTournament(TournamentMode):
	"""
	Single-elimination tournament
	https://en.wikipedia.org/wiki/Single-elimination_tournament
	"""
	_name = "Single-elimination Tournament"
	_HTMLoptions = """
	Nb groups: <input name="nbGroups" type="number" required/><br/>
	Nb first in group <input name="first" type="number" required/>
	"""


