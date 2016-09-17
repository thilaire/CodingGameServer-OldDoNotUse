"""
Webserver functions

"""

from bottle import route,  jinja2_view, request, redirect, static_file, template, TEMPLATE_PATH, response, error
from functools import partial
from Player import Player
from Labyrinth import Labyrinth
from logging import getLogger

logger = getLogger('bottle')

#configure the web server template engine
view = partial(jinja2_view, template_lookup=['templates'])
TEMPLATE_PATH.append( 'templates' )


@route('/')
@route('/index.html')
@view("index.html")
def index():
	"""
	Main page (based on index.html template)
	"""
	HTMLPlayerList = "\n".join([ "<li>"+ p.HTMLrepr() + "</li>\n" for p in Player.allPlayers.values()])
	HTMLGameList = "\n".join(["<li>" + l.HTMLrepr() + "</li>\n" for l in Labyrinth.allGames.values()])
	return {"ListOfPlayers":HTMLPlayerList, "ListOfGames": HTMLGameList}


@route('/new_game')
@view("new_game.html")
def new_game():
	"""
	Page to create a new game
	"""
	Players = "\n".join(["<option>" + p.name + "</option>\n" for p in Player.allPlayers.values()])

	return { "list_players": Players}


@route('/create_new_game', method='POST')
def create_new_game():
	"""
	Page to create a new game
	"""
	# get Player 1
	player1 = Player.getFromName( request.forms.get('player1') )
	player2 = Player.getFromName( request.forms.get('player2') )

	# the constructor will check if player1 and player2 are available to play
	g = Labyrinth( player1, player2 )

	if g is None:
		#TODO: redirect to an error page
		#TODO: log this
		return "Erreur. Impossible de créer une partie avec " + request.forms.get('player1') + " and " + request.forms.get('player2')
	else:
		redirect('/')




@route('/game/<gameName>')
def game(gameName):
	g = Labyrinth.getFromName( gameName)
	if g:
		#TODO: use a template, and call for g.fullData() that returns a dictionary with all the possible informations about the game
		return g.HTMLpage()
	else:
		return template('noGame.html', gameName=gameName)


@route('/player/<playerName>')
def player(playerName):
	pl = Player.getFromName( playerName)
	if pl:
		#TODO: use a template
		return pl.HTMLpage()
	else:
		return template('noPlayer.html', player=playerName)



# display the logs
@route('/logs')
def log():
	return static_file('activity.log', root='logs/')


@route('/logs/player/<playerName>')
def log(playerName):
	return static_file(playerName+'.log', root='logs/players/')


@error(404)
@view('error404.html')
def error404(error):
	#TODO: log this
	return {'url':request.url}


@error(500)
def errror500(error):
	logger.error(error)
	return "We have an unexpected error. It has been reported, and we will work on it so that it never occurs again !"