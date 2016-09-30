"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev... (not even a beta)

File: webserver.py
	Contains the webserver routines (based on bottle)
	-> all the routes are defined here
	-> the template files used are in templates

"""

from logging import getLogger

from bottle import route, request, jinja2_view as view, redirect, static_file, jinja2_template as template, TEMPLATE_PATH, error, abort
from bottle import run, response, install			    # webserver (bottle)
from os.path import isfile, join
from CGS.Game import Game
from CGS.Player import Player

from functools import wraps										# use to wrap a logger for bottle

# global variables
weblogger = getLogger('bottle')
theGame = Game          # class of the Game used (should at least inherit from Game; set by runWebServer function)


# Path to the template (it will be completed with <gameName>/server/templates/)
TEMPLATE_PATH[:] = ['CGS/templates']


def runWebServer(host, port, quiet, gameClass):
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

	# keep the gameClass
	global theGame
	theGame = gameClass
	#update the template paths so that in priority, it first looks in <gameName>/server/templates/ and then in CGS/server/templates
	TEMPLATE_PATH.append(gameClass.__name__ + "/server/templates")
	TEMPLATE_PATH.reverse()
	# Start the web server
	install(log_to_logger)
	weblogger.info("Run the web server on port %d...", port)
	run(host=host, port=port, quiet=quiet)


def static_file_from_templates(fileName):
	"""
	Returns a static_file from the template paths
	The function first searches in the first path of the template path list (TEMPLATE_PATH). If the file exists, the function
	returns that file (static_file function), otherwise it searches for the file in the next path...
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


@route('/')
@route('/index.html')
@view("index.html")
def index():
	"""
	Main page (based on index.html template)
	"""
	HTMLPlayerList = "\n".join(["<li>" + p.HTMLrepr() + "</li>\n" for p in Player.allPlayers.values()])
	HTMLGameList = "\n".join(["<li>" + l.HTMLrepr() + "</li>\n" for l in Game.allGames.values()])
	return {"ListOfPlayers": HTMLPlayerList, "ListOfGames": HTMLGameList}


@route('/new_game')
@view("new_game.html")
def new_game():
	"""
	Page to create a new game
	"""
	Players = "\n".join(["<option>" + p.name + "</option>\n" for p in Player.allPlayers.values()])

	return {"list_players": Players}


@route('/create_new_game', method='POST')
def create_new_game():
	"""
	Page to create a new game
	"""
	# get Player 1
	player1 = Player.getFromName(request.forms.get('player1'))
	player2 = Player.getFromName(request.forms.get('player2'))


	try:
		# the constructor will check if player1 and player2 are available to play
		# no need to store the labyrinth object created here
		theGame(player1, player2)

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
		# TODO: use a template, and call for g.fullData() that returns a dictionary with all the possible informations about the game
		return g.HTMLpage()
	else:
		return template('noGame.html', gameName=gameName)


@route('/player/<playerName>')
def player(playerName):
	pl = Player.getFromName(playerName)
	if pl:
		# TODO: use a template
		return pl.HTMLpage()
	else:
		return template('noPlayer.html', player=playerName)


# display the logs
@route('/logs')
def log():
	return static_file('activity.log', root=theGame.__name__+'/logs/')


@route('/logs/player/<playerName>')
def log(playerName):
	return static_file(playerName+'.log', root=theGame+'/logs/players/')


@route('/logs/game/<gameName>')
def log(gameName):
	return static_file(gameName+'.log', root=theGame+'/logs/games/')



# handle errors
@error(404)
@view('error404.html')
def error404():
	# TODO: log this
	return {'url': request.url}


@error(500)
def errror500(err):
	# TODO: useful ? to be checked
	weblogger.error(err)
	return "We have an unexpected error. It has been reported, and we will work on it so that it never occurs again !"
