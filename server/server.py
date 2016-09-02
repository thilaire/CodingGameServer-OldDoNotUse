#coding: utf8

from socketserver import ThreadingTCPServer, BaseRequestHandler
from bottle import Bottle, route, run, jinja2_view, install
from functools import partial, wraps
import threading
from Player import Player

class connectionError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)



class PlayerSocketHandler(BaseRequestHandler):
	"""
	The request handler class for our server.

	It is instantiated once per connection to the server.
	"""
	def handle(self):

		self._player = None
		try:
			name = self.getPlayerName()
			self._player = Player( name )

			while True:
				data = str( self.request.recv(1024).strip(), "utf-8" )
				if data.startswith("GET_LAB:"):
					#retrieve data command
					print("Not yet implemented...")
					pass
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

			print( "Error with %s: '%s'"%(self._player.name if self._player is not None else "None", e) )


	def finish(self):
		"""
		Call when the connection is closed
		"""
		if self._player is not None:
			Player.removePlayer(self._player.name)
			del self._player

			print ("Chéri, ça a coupé...")


	def getPlayerName(self):
		"""
		receive and treat connection to get the player name
		:return:
		the player name
		or raises an exception (connectionError)
		"""
		data = str( self.request.recv(1024).strip(), "utf-8" )
		print( "Receive: '"+data+"'" )
		if not data.startswith("CLIENT_NAME: "):
			raise connectionError( "Bad protocol, should start with CLIENT_NAME: ")

		#TODO: créer le joueur ICI et vérifier que tout marche

		# just send back the same data, but upper-cased
		print( "Send: OK")
		self.request.sendall(b"OK")
		return data[13:]



view = partial(jinja2_view, template_lookup=['templates'])




@route('/')
@view("index.html")
def index():
	HTMLlist = "\n".join([ "<li>"+ p.HTMLrepr()+"</li>\n" for p in Player.allPlayers.values()])

	return {"ListOfPlayers":HTMLlist}





HOST = "localhost"
PLAYER_PORT = 1234
WEB_PORT = 8000

# Start the web server
threading.Thread(target=run, kwargs={ 'server':'paste', 'host':HOST, 'port':WEB_PORT}).start()


# Start Socket server (connection to players)
PlayerServer = ThreadingTCPServer((HOST, PLAYER_PORT), PlayerSocketHandler)
print( "Run the socket server...")
threading.Thread( target=PlayerServer.serve_forever() )


