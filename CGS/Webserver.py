"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev...

File: webserver.py
	Contains the webserver routines (based on bottle)
	-> all the routes are defined here
	-> the template files used are in templates

"""
from gevent import monkey
monkey.patch_all()

from logging import getLogger
import threading
from bottle import route, request, jinja2_view as view, jinja2_template as template
from bottle import redirect, static_file, TEMPLATE_PATH, error, abort
from bottle import run, response, install, default_app		# webserver (bottle)
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError
from os.path import isfile, join
from functools import wraps										# use to wrap a logger for bottle
from CGS.Game import Game
from CGS.RegularPlayer import RegularPlayer
from CGS.Logger import Config
from CGS.Tournament import Tournament
from CGS import TournamentMode        # HERE we import all the tournaments type (DO NOT REMOVE)
from CGS.WebSocketBase import WebSocketBase


# weblogger
weblogger = getLogger('bottle')

# Path to the template (it will be completed with <gameName>/server/templates/)
TEMPLATE_PATH[:] = ['CGS/templates']


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
	TEMPLATE_PATH.append(Game.getTheGameName() + "/server/templates")
	TEMPLATE_PATH.reverse()
	# Start the web server
	install(log_to_logger)
	weblogger.message("Run the web server on port %d...", port)

	default_app().catchall = True       # all the exceptions/errors are catched, and re-routed to error500
	run(host=host, port=port, quiet=quiet, server='gevent', handler_class=WebSocketHandler)


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
	return static_file_from_templates('favicon.ico')


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
	return {"GameName": Game.getTheGameName(),
	        'SocketName': '"ws://localhost:8088/websocket/ListOfInstances"'}


# =======
#  Games
# =======
@route('/new_game')     # TODO: route vers xxx.html au lieu de xxx !
@view("new_game.html")
def new_game():
	"""
	Page to create a new game
	"""
	Players = "\n".join(["<option>" + p.name + "</option>\n" for p in RegularPlayer.allInstances.values()])

	return {"list_players": Players}


@route('/create_new_game', method='POST')
def create_new_game():
	"""
	Receive the form to create a new game
	-> create the game (ie runPhase it)
	"""
	# get Players
	player1 = RegularPlayer.getFromName(request.forms.get('player1'))
	player2 = RegularPlayer.getFromName(request.forms.get('player2'))

	# TODO: add some options (timeout, seed, etc.) in the html, and send them to the constructor
	try:
		# the constructor will check if player1 and player2 are available to play
		# no need to store the game object created here
		Game.getTheGameClass()(player1, player2)

	except ValueError as e:
		# TODO: redirect to an error page
		# TODO: log this
		return "Error. Impossible to create a game with " + request.forms.get('player1') + " and " + request.forms.get('player2') + ": '" + str(e) + "'"
	else:
		redirect('/')


@route('/game/<gameName>')
def game(gameName):
	g = Game.getFromName(gameName)
	if g:
		return template('Game.html', SocketName='ws://localhost:8088/game/websocket/'+gameName, **g.HTMLdict())
	else:
		return template('noGame.html', gameName=gameName)


@route('/game/websocket/<gameName>')
def gameWebSocket(gameName):
	g = Game.getFromName(gameName)
	if g:
		wsock = request.environ.get('wsgi.websocket')
		if not wsock:
			abort(400, "Expected Websocket request.")
		g.addsock(wsock)
		g.send_wsock()
		while True:
			try:
				wsock.receive()     # we do not care about the answer
			except WebSocketError:
				g.removesock(wsock)
				break
	else:
		return template('noGame.html', gameName=gameName)


# ============
#  Tournament
# ============
@route('/new_tournament')
@view("new_tournament.html")
def new_tournament():
	"""
	Page to create a new tournament
	Build from HTMLFormDict class method of TournamentMode (build from all the tournament modes)
	"""
	return Tournament.HTMLFormDict()


@route('/create_new_tournament', method='POST')
def create_new_tournament():
	"""
	Receive the form to create a new tournament
	"""
	# create the tournament
	try:
		Tournament.factory(**dict(request.forms))
	except ValueError as e:
		# TODO: redirect to an error page
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
		return template('tournament.html', {'t': t})
	else:
		return template('noTournament.html', tournamentName=tournamentName)


@route('/run_tournament/<tournamentName>', method='POST')
def runTournament(tournamentName):
	"""
	Receive the runPhase tournament form
	redirect to `tournament/<tournamentName>` if tournament exists (otherwise `noTournament.html`)
	Parameters:
	- tournamentName: name of the tournament
	"""
	t = Tournament.getFromName(tournamentName)
	if t:
		threading.Thread(target=t.runPhase).start()
		redirect('/tournament/'+tournamentName)
	else:
		return template('noTournament.html', tournamentName=tournamentName)


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
		return pl.HTMLpage()
	else:
		return template('noPlayer.html', player=playerName)


# ==========
# Websockets
# ==========
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
	# check if that instance exists
	WebSocketBase.registerLoIWebSocket(wsock)
	WebSocketBase.sendListofInstances()      # TODO: it is not necessary to send the information to all the other sockets (only this one)
	while True:
		try:
			msg = wsock.receive()
		except WebSocketError:
			WebSocketBase.removeLoIWebSocket(wsock)
			break


# ======
#  logs
# =======

@route('/logs')
def log():
	return static_file('activity.log', root=Config.logPath)


@route('/logs/player/<playerName>')
def logP(playerName):
	return static_file(playerName+'.log', root=join(Config.logPath, 'players'))


@route('/logs/game/<gameName>')
def logG(gameName):
	return static_file(gameName+'.log', root=join(Config.logPath, 'games'))


# =======
#  errors
# ========
@error(404)
@view('error404.html')
def error404():
	# TODO: log this
	return {'url': request.url}
#
#
# @error(500)
# def errror500(err):
# 	# TODO: useful ? to be checked
# 	weblogger.error(err, exc_info=True)
#
# 	return "We have an unexpected error. It has been reported, and we will work on it so that it never occurs again !"



