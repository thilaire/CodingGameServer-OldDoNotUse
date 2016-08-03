


class Player:
	allPlayers = {}

	def __init__(self, name):
		print("Add a new player: "+name)
		self._name = name
		self.allPlayers[name] = self

	def HTMLrepr(self):
		return "<B>"+self._name+"</B>"

	@classmethod
	def removePlayer(cls, name):
		print( "on coupe" )
		del cls.allPlayers[name]

	@property
	def name(self):
		return self._name

