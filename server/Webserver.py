"""
* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL

File: webserver.py
	Contains the webserver routines (based on bottle)
	-> all the routes are defined here
	-> the template files used are in templates

Copyright 2016-2017 T. Hilaire, J. Brajard
"""


from gevent import monkey
monkey.patch_all()

from logging import getLogger
import threading
from bottle import route, request, jinja2_view as view, jinja2_template as template
from bottle import Jinja2Template
from bottle import redirect, static_file, TEMPLATE_PATH, error, abort
from bottle import run, response, install, default_app		# webserver (bottle)
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError
from os.path import isfile, join
from functools import wraps										# use to wrap a logger for bottle
from server.Game import Game
from server.Player import RegularPlayer
from server.Logger import Config
from server.Tournament import Tournament
from server.BaseClass import BaseClass

# weblogger
weblogger = getLogger('bottle')

# Path to the template (it will be completed with <gameName>/server/templates/)
TEMPLATE_PATH[:] = ['server/templates']


def runWebServer(host, port, quiet):
	"""
	Install the logger and run the webserver
	"""
	# add a logger wrapper for bottle (in order to log its activity)
	# See http://stackoverflow.com/questions/31080214/python-bottle-always-logs-to-console-no-logging-to-file
	def log_to_logger(fn):
		"""	Wrap a Bottle request so that a log line is emitted after it's handled."""
		@wraps(fn)
		def _log_to_logger(*_args, **_kwargs):
			actual_response = fn(*_args, **_kwargs)
			weblogger.info('%s %s %s %s' % (request.remote_addr, request.method, request.url, response.status))
			return actual_response
		return _log_to_logger


	# update the template paths so that in priority,
	# it first looks in <gameName>/server/templates/ and then in CGS/server/templates
	TEMPLATE_PATH.append('games/' + Game.getTheGameName() + "/server/templates/")
	TEMPLATE_PATH.reverse()
	# add the base url to all the templates
	Jinja2Template.defaults['base_url'] = 'http://%s:%s/' % (host, port)
	# Start the web server
	install(log_to_logger)
	weblogger.message("Run the web server on port %d...", port)

	default_app().catchall = True       # all the exceptions/errors are catched, and re-routed to error500
	run(host=host, port=port, quiet=quiet, server='gevent', handler_class=WebSocketHandler)


# ================
#   static files
# ================
def static_file_from_templates(fileName):
	"""
	Returns a static_file from the template paths
	The function first searches in the first path of the template path list (TEMPLATE_PATH).
	If the file exists, the function returns that file (static_file function), otherwise it searches
	for the file in the next path...
	Redirects to error 404 if the file is not found.
	"""
	for path in TEMPLATE_PATH:
		if isfile(join(path, fileName)):
			return static_file(fileName, path)
	abort(404)


# some static files
@route('/favicon.ico')
def favicon():
	"""Returns the favicon"""
	return static_file_from_templates('favicon.ico')


@route('/style.css')
def css():
	"""Returns the CSS style"""
	return static_file_from_templates('style.css')


@route('/banner.png')
def banner():
	"""Returns the pages top banner PNG file"""
	return static_file_from_templates('banner.png')


# ================
#   main page
# ================
@route('/')
@route('/index.html')
@view("index.html")
def index():
	"""
	Main page (based on index.html template)
	"""
	return {"GameName": Game.getTheGameName(), 'host': Config.host, 'webPort': Config.webPort}


# =======
#  Games
# =======
@route('/new_game.html')
@view("game/new_game.html")
def new_game():
	"""
	Page to create a new game
	"""
	Players = "\n".join(["<option>" + p.name + "</option>\n" for p in RegularPlayer.allInstances.values()])

	return {"GameName": Game.getTheGameName(), "list_players": Players}


@route('/create_new_game.html', method='POST')
def create_new_game():
	"""
	Receive the form to create a new game
	-> create the game (ie runPhase it)
	"""
	# get Players
	player1 = RegularPlayer.getFromName(request.forms.get('player1'))
	player2 = RegularPlayer.getFromName(request.forms.get('player2'))

	# !TODO: add some options (timeout, seed, etc.) in the html, and send them to the constructor
	try:
		# the constructor will check if player1 and player2 are available to play
		# no need to store the game object created here
		Game.getTheGameClass()(player1, player2)

	except ValueError as e:
		# !TODO: redirect to an error page
		# TODO: log this
		return "Error. Impossible to create a game with " + str(request.forms.get('player1')) + " and " + str(request.forms.get('player2')) + ": '" + str(e) + "'"
	else:
		redirect('/')


@route('/game/<gameName>')
def game(gameName):
	"""Returns the webpage of a game
	<gameName> is the name of the game
	If the name is not valid, the answer with the noObject page
	"""
	g = Game.getFromName(gameName)

	if g:
		try:
			displayName = g.getCutename()
		except NotImplementedError:
			displayName = gameName
		return template('game/Game.html', host=Config.host, webPort=Config.webPort,
		                gameName=displayName, player1=g.players[0].HTMLrepr(), player2=g.players[1].HTMLrepr())
	else:
		return template('noObject.html', className='game', objectName=gameName)


# ============
#  Tournament
# ============
@route('/new_tournament.html')
@view("tournament/new_tournament.html")
def new_tournament():
	"""
	Page to create a new tournament
	Build from HTMLFormDict class method of TournamentMode (build from all the tournament modes)
	"""
	return Tournament.HTMLFormDict(Game.getTheGameName())


@route('/create_new_tournament.html', method='POST')
def create_new_tournament():
	"""
	Receive the form to create a new tournament
	"""
	# create the tournament
	try:
		Tournament.factory(**dict(request.forms))
	except ValueError as e:
		# !TODO: redirect to an error page
		# TODO: log this
		return "Error. Impossible to create a tournament with " + str(dict(request.forms)) + ":'" + str(e) + "'"
	else:
		redirect('/')


@route('/tournament/<tournamentName>')
def tournament(tournamentName):
	"""
	Web page for a tournament
	redirect to `noTournament.html` if tournament doesn't exist
	Parameters:
	- tournamentName: name of the tournament
	"""
	t = Tournament.getFromName(tournamentName)
	if t:
		return template('tournament/tournament.html', {'t': t, 'host': Config.host, 'webPort': Config.webPort})
	else:
		return template('noObject.html', className='tournament', objectName=tournamentName)



@route('/run_tournament/<tournamentName>', method='POST')
def runTournament(tournamentName):
	"""
	Receive the runPhase tournament form
	redirect to `noTournament.html` if the tournament doesn't exit
	other, return nothing, since it is run from ajax (doesn't wait for any response)
	Parameters:
	- tournamentName: name of the tournament
	"""
	t = Tournament.getFromName(tournamentName)
	if t:
		threading.Thread(target=t.runPhase, kwargs=dict(request.forms)).start()
	else:
		return template('noObject.html', className='tournament', objectName=tournamentName)


# =========
#  Player
# =========

@route('/player/<playerName>')
def player(playerName):
	"""
	Web page for a player
	Redirects to `noPlayer.html` if the player doesn't exist
	"""
	pl = RegularPlayer.getFromName(playerName)
	if pl:
		# TODO: use a template
		return template('player/Player.html', host=Config.host, webPort=Config.webPort,
		                playerName=playerName)
	else:
		return template('noObject.html', className='player', objectName=playerName)



@route('/player/disconnect/<playerName>')
def disconnectPlayer(playerName):
	"""
	Disconnect a player
	Only for debug...
	:param playerName:
	:return:
	"""
	# !FIXME: activate this only in debug or dev mode
	# TODO: if necessary, add a disconnectAllPlayer
	pl = RegularPlayer.getFromName(playerName)
	if pl:
		pl.disconnect()
		redirect('/')
	else:
		return template('noObject.html', className='player', objectName=playerName)

# ==========
# Websockets
# ==========
# TODO: can be directly obtained from {x.__name__:x for x in WebSocket.__subclasses__()}
wsCls = {'Game': Game, 'Player': RegularPlayer, 'Tournament': Tournament}


@route('/websocket/ListOfInstances')
def classWebSocket():
	"""
	Websocket for the list of instances of the classes Game, Player and Tournament
	-> used to get the a json with the list of instances of theses classes

	"""
	# should be a websocket
	wsock = request.environ.get('wsgi.websocket')
	if not wsock:
		abort(400, "Expected Websocket request.")
	# register this websocket
	BaseClass.registerLoIWebSocket(wsock)
	# send to this websocket
	BaseClass.sendListofInstances(wsock)
	# loop until the end of this websocket
	while True:
		try:
			wsock.receive()
		except WebSocketError:
			BaseClass.removeLoIWebSocket(wsock)
			break


@route('/websocket/<clsName>/<name>')
def classWebSocket(clsName, name):
	"""
	Websocket for an instance of the classes Game, Player or Tournament
	-> used to get the a json with informations about this object

	"""
	# should be a websocket
	wsock = request.environ.get('wsgi.websocket')
	if not wsock:
		abort(400, "Expected Websocket request.")
	# check if that instance exists
	if clsName not in wsCls:
		abort(400, "Invalid class %s is not in %s" % (clsName, wsCls.keys()))
	cls = wsCls[clsName]
	obj = cls.getFromName(name)
	if obj is None:
		abort(400, "Invalid name (%s) for class %s" % (name, clsName))
	# register this websocket
	obj.registerWebSocket(wsock)
	# send to this websocket
	obj.sendUpdateToWebSocket(wsock)
	# loop until the end of this websocket
	while True:
		try:
			wsock.receive()
		except WebSocketError:
			BaseClass.removeLoIWebSocket(wsock)
			break


# ======
#  logs
# =======

@route('/logs')
def log():
	"""Returns the activity.log file"""
	return static_file('activity.log', root=Config.logPath)


@route('/logs/player/<playerName>')
def logP(playerName):
	"""
	Returns a player log file
	:param playerName: (string) name of the player
	"""
	return static_file(playerName+'.log', root=join(Config.logPath, 'players'))


@route('/logs/game/<gameName>')
def logG(gameName):
	"""
	Returns a game log file
	:param gameName: (string) name of the game
	"""
	return static_file(gameName+'.log', root=join(Config.logPath, 'games'))


# ================
#   info page
# ================
@route('/about.html')
@view("about.html")
def index():
	"""
	Main page (based on index.html template)
	"""
	return {"GameName": Game.getTheGameName()}


# =======
#  errors
# ========
@error(404)
@view('error404.html')
def error404():
	"""Returns error 404 page"""
	# TODO: log this
	return {'url': request.url}
#
#
# @error(500)
# def errror500(err):
# 	# !TODO: useful ? to be checked
# 	weblogger.error(err, exc_info=True)
#
# 	return "We have an unexpected error. It has been reported, and we will work on it so that it never occurs again !"



