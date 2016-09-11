"""
Webserver functions

"""

from bottle import route,  jinja2_view, request, redirect, static_file, template, TEMPLATE_PATH, response, error
from functools import partial
from Player import Player
from Game import Game

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
	HTMLGameList = "\n".join(["<li>" + g.HTMLrepr() + "</li>\n" for g in Game.allGames.values()])
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

	if player1 and player2 and player1 is not player2:
		g = Game( player1, player2 )

	redirect('/')




@route('/game/<gameName>')
def game(gameName):
	g = Game.getFromName( gameName)
	if g:
		return g.HTMLpage()
	else:
		return template('noGame.html', player=gameName)


@route('/player/<playerName>')
def player(playerName):
	pl = Player.getFromName( playerName)
	if pl:
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
	return {'url':request.url}