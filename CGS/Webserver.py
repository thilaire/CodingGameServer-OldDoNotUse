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

from logging import getLogger

from bottle import route, request, jinja2_view as view, jinja2_template as template
from bottle import redirect, static_file, TEMPLATE_PATH, error, abort
from bottle import run, response, install, default_app			    # webserver (bottle)
from os.path import isfile, join
from functools import wraps										# use to wrap a logger for bottle
from CGS.Game import Game
from CGS.RegularPlayer import RegularPlayer
from CGS.Logger import Config
from CGS.Tournament import Tournament

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
	run(host=host, port=port, quiet=quiet)



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


@route('/')
@route('/index.html')
@view("index.html")
def index():
	"""
	Main page (based on index.html template)
	"""
	HTMLPlayerList = "\n".join(["<li>" + p.HTMLrepr() + "</li>\n" for p in RegularPlayer.allPlayers.values()])
	HTMLGameList = "\n".join(["<li>" + l.HTMLrepr() + "</li>\n" for l in Game.allGames.values()])
	HTMLTournamentList = "\n".join(["<li>" + l.HTMLrepr() + "</li>\n" for l in Tournament.allTournaments.values()])
	return {"ListOfPlayers": HTMLPlayerList, "ListOfGames": HTMLGameList,
	        "GameName": Game.getTheGameName(), "ListOfTournaments": HTMLTournamentList}


# TODO: route vers xxx.html au lieu de xxx !

@route('/new_game')
@view("new_game.html")
def new_game():
	"""
	Page to create a new game
	"""
	Players = "\n".join(["<option>" + p.name + "</option>\n" for p in RegularPlayer.allPlayers.values()])

	return {"list_players": Players}


@route('/create_new_game', method='POST')
def create_new_game():
	"""
	Receive the form to create a new game
	-> create the game (ie run it)
	"""
	# get Players
	player1 = RegularPlayer.getFromName(request.forms.get('player1'))
	player2 = RegularPlayer.getFromName(request.forms.get('player2'))

	# TODO: add some options (timeout, seed, etc.) in the html, and send them to the constructor
	try:
		# the constructor will check if player1 and player2 are available to play
		# no need to store the labyrinth object created here
		Game.getTheGameClass()(player1, player2)

	except ValueError as e:
		# TODO: redirect to an error page
		# TODO: log this
		return "Error. Impossible to create a game with " + request.forms.get('player1') + " and " + request.forms.get('player2') + ": '" + str(e) + "'"
	else:
		redirect('/')



@route('/new_tournament')
@view("new_tournament.html")
def new_tournament():
	"""
	Page to create a new tournament
	"""
	return {}   # empty dictionary for the moment


@route('/create_new_tournament', method='POST')
def create_new_tournament():
	"""
	Receive the form to create a new tournament
	"""
	# get the options
	name = request.forms.get('name')
	nbMaxPlayers = request.forms.get('nbMaxPlayers')
	rounds = request.forms.get('rounds')
	mode = request.forms.get('mode')

	# create the tournament
	d = {'name': name, 'nbMaxPlayers': nbMaxPlayers, 'rounds': rounds, 'mode': mode}
	try:
		# or directly pass request.form...
		t = Tournament(**d)
	except ValueError as e:
		# TODO: redirect to an error page
		# TODO: log this
		return "Error. Impossible to create a tournament with " + str(d) + ":'" + str(e) + "'"
	else:
		redirect('/')


@route('/tournament/<tournamentName>')
def tournament(tournamentName):
	t = Tournament.getFromName(tournamentName)
	if t:
		return t.HTMLpage()
	else:
		return template('noTournament.html')


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
	pl = RegularPlayer.getFromName(playerName)
	if pl:
		# TODO: use a template
		return pl.HTMLpage()
	else:
		return template('noPlayer.html', player=playerName)


# display the logs
@route('/logs')
def log():
	return static_file('activity.log', root=Config.logPath)


@route('/logs/player/<playerName>')
def logP(playerName):
	return static_file(playerName+'.log', root=join(Config.logPath, 'players'))


@route('/logs/game/<gameName>')
def logG(gameName):
	return static_file(gameName+'.log', root=join(Config.logPath, 'games'))


# handle errors
@error(404)
@view('error404.html')
def error404():
	# TODO: log this
	return {'url': request.url}


@error(500)
def errror500(err):
	# TODO: useful ? to be checked
	weblogger.error(err, exc_info=True)

	return "We have an unexpected error. It has been reported, and we will work on it so that it never occurs again !"
