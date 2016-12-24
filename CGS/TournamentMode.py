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
	Contains the class Tournament
	-> defines the generic Tournament's behavior

"""


class TournamentMode:
	# to be overloaded
	_name = ""

	def __init__(self):
		pass


	@classmethod
	def HTMLSelect(cls):
		"""
		Returns an HTML string, containing a <SELEC> element to be included in HTML file
		It's a drop-down list with all the existing modes
		"""
		st = "<select name='mode'>\n"
		st += "\n".join("<option value='%s'>%s</option>" % (sc._name, sc._name) for sc in cls.__subclasses__())
		return st + "\n</select>"


	@classmethod
	def getFromName(cls, name):
		"""
		Get a tournament mode from its name
		Parameter:
		- name: (string) name of the mode we want to get
		Returns the Tournament mode, or None if it doesn't exist
		"""
		d = {sc._name: sc for sc in cls.__subclasses__()}
		return d.get(name, None)


class Championship(TournamentMode):
	"""
	Championship mode
	"""
	_name = "Championship"
	pass


class SingleEliminationTournament(TournamentMode):
	"""
	Single-elimination tournament
	https://en.wikipedia.org/wiki/Single-elimination_tournament
	"""
	_name = "Single-elimination Tournament"
	pass

