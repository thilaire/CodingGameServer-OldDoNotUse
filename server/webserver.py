"""
Webserver functions

"""

from bottle import route,  jinja2_view, request, redirect, static_file
from functools import partial
from Player import Player

#configure the web server template engine
view = partial(jinja2_view, template_lookup=['templates'])



@route('/')
@route('index.html')
@view("index.html")
def index():
	"""
	Main page (based on index.html template)
	"""
	HTMLlist = "\n".join([ "<li>"+ p.HTMLrepr() + "</li>\n" for p in Player.allPlayers.values()])

	return {"ListOfPlayers":HTMLlist}


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
	#player1 = Player.getFromName( request.forms.get('player1') )

	#player2 = Player.getFromName( request.forms.get('player2') )


	return redirect("/")




@route('/logs')
def log():
	return static_file('activity.log', root='logs/')

