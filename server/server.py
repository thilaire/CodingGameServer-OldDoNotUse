#coding: utf8

import SocketServer
from bottle import Bottle, route, run, jinja2_view, install
from functools import partial, wraps
import threading



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
		print "on coupe"
		del cls.allPlayers[name]








class MyTCPHandler(SocketServer.BaseRequestHandler):
	"""
	The request handler class for our server.

	It is instantiated once per connection to the server.
	"""
	def handle(self):
		# self.request is the TCP socket connected to the client
		self.data = self.request.recv(1024).strip()
		self._player = None
		print "Receive: '"+self.data+"'"
		if not self.data.startswith("CLIENT_NAME: "):

			self.request.sendall( "Bad protocol, should start with CLIENT_NAME: ")
			print "Send: '"+"Bad protocol, should start with CLIENT_NAME: "+"'"
			return
		name = self.data[13:]
		self._player = Player( name )
		# just send back the same data, but upper-cased
		print "Send: OK"
		self.request.sendall("OK")
		while True:
			pass

	def finish(self):
		"""
		Call when the connection is closed
		"""
		if self._player is not None:
			Player.removePlayer(self._player._name)
			del self._player

			print "Chéri, ça a coupé..."





view = partial(jinja2_view, template_lookup=['templates'])




@route('/')
@view("index.html")
def index():
	HTMLlist = "\n".join([ "<li>"+ p.HTMLrepr()+"</li>\n" for p in Player.allPlayers.itervalues()])
	print "HTMList="+HTMLlist
	return {"ListOfPlayers":HTMLlist}





HOST = "localhost"
PLAYER_PORT = 1234
WEB_PORT = 8000

# Start the web server
#threading.Thread(target=run, kwargs={'server':'paste', 'host':HOST, 'port':WEB_PORT}).start()


# Start Socket server (connection to players)
PlayerServer = SocketServer.TCPServer((HOST, PLAYER_PORT), MyTCPHandler)
threading.Thread( target=PlayerServer.serve_forever() )


