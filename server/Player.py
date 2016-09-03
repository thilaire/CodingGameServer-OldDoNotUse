


class Player:
	allPlayers = {}

	def __init__(self, name):
		print("Add a new player: "+name)
		self._name = name
		self.allPlayers[name] = self
		self._state = "send:setup"

	def HTMLrepr(self):
		return "<B>"+self._name+"</B>"

	def HTMLstatus(self):
		if self._state == "send:setup":
			return "se connecte..."
		elif self._state == "rcv:lab":
			return "attend un adversaire"
	@classmethod
	def removePlayer(cls, name):
		print( "on coupe" )
		del cls.allPlayers[name]

	def setstate(self,newstate):
		print(self._name,": new state -> ",newstate)
		self._state = newstate
        
	@property
	def name(self):
		return self._name

