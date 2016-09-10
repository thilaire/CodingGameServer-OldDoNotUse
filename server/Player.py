import logging
from socketserver import ThreadingTCPServer, BaseRequestHandler


logger = logging.getLogger()


class connectionError(Exception):
	"""stupid class to manage the errors due to the connection
	"""
	# TODO: Usefull ?
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)



class PlayerSocketHandler(BaseRequestHandler):
	"""
	The request handler class for our server.
	It is instantiated once per connection to the server, ie one per player
	"""
	def handle(self):

		self._player = None
		try:
			name = self.getPlayerName()
			self._player = Player( name )

			while True:
				data = str( self.request.recv(1024).strip(), "utf-8" )
				logger.debug( "Receive '%s' from player %s (%s)"%( data, self._player.name, self.client_address ))

				if data.startswith("GET_LAB:"):
					#retrieve data command
					print("Not yet implemented...")
					pass
				elif data.startswith("WAIT_ROOM:"):
					self._player.setstate("rcv:lab")
					self.request.sendall(b"OK")

				elif data.startswith("GET_MOVE:"):
					# get move of the opponent
					print("Not yet implemented...")
					pass
				elif data.startswith("PLAY_MOVE:"):
					# play move
					print("Not yet implemented...")
					pass
				elif data.startswith("WAIT_START:"):
					# wait start
					print("Not yet implemented...")
					pass
				elif data.startswith("DISP_LAB:"):
					# ask for display
					self.request.sendall(b"OK")
					self.request.sendall( b"TOOTOTOOTOOOOT\n")
				else:
					raise connectionError("Bad protocol, command should not start with '"+data+"'")

		except connectionError as e:
			logger.error( "Error with %s: '%s'"%(self.playerNameAdress, e) )


	def finish(self):
		"""
		Call when the connection is closed
		"""
		if self._player is not None:
			logger.debug("Connection closed with player "+self.playerNameAdress)
			Player.removePlayer(self._player.name)
			del self._player




	def getPlayerName(self):
		"""
		receive and treat connection to get the player name
		:return:
		the player name
		or raises an exception (connectionError)
		"""
		data = str( self.request.recv(1024).strip(), "utf-8" )
		logger.debug( "Receive: '"+data+"' from client "+self.client_address[0] )
		if not data.startswith("CLIENT_NAME: "):
			raise connectionError( "Bad protocol, should start with CLIENT_NAME: ")

		#TODO: créer le joueur ICI et vérifier que tout marche

		# just send back the same data, but upper-cased
		self.request.sendall(b"OK")
		logger.debug( "Send OK to player " + self.playerNameAdress)
		return data[13:]

	@property
	def playerNameAdress(self):
		return "%s (%s)"%( self._player.name if self._player is not None else "None", self.client_address[0])




class Player:
	allPlayers = {}

	def __init__(self, name):
		logger.debug( name + " just log in.")
		self._name = name
		self.allPlayers[name] = self
		#self._state = "send:setup"

	def HTMLrepr(self):
		return "<B>"+self._name+"</B>"

	# def HTMLstatus(self):
	# 	if self._state == "send:setup":
	# 		return "se connecte..."
	# 	elif self._state == "rcv:lab":
	# 		return "attend un adversaire"


	@classmethod
	def removePlayer(cls, name):
		logger.debug( name +" just log out.")
		del cls.allPlayers[name]


	@classmethod
	def getFromName(cls, name):
		"""
		Get a player form its name
		:param name: (string) name of the player
		:return: the player (the object) or None if this player doesn't exist
		"""
		return cls.allPlayers.get( name, None)



	def setstate(self,newstate):
		print(self._name,": new state -> ",newstate)
		self._state = newstate

	@property
	def name(self):
		return self._name

