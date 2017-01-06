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
		options = "\n".join('<div display="none" id="%s">%s</div>' % (sc.__name__, sc._HTMLoptions) for sc in cls.__subclasses__())

		# JavascriptModeOptions
		jOptions = "\n".join('document.getElementById("%s").style.display="none";' % (sc.__name__) for sc in cls.__subclasses__())

		return { "HTMLmodes": modes, "HTMLmodeOptions": options, "JavascriptModeOptions": jOptions}



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




class Championship(TournamentMode):
	"""
	Championship mode
	"""
	_name = "Championship"
	_HTMLoptions = ""



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


