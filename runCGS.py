#!/usr/bin/env python3
# -*- coding: utf-8
"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *


Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev...

File: runCGS.py
	Main file/entry for the Coding Game Server


CGS requires Python3 and the following packages: colorama, colorlog, docopt, bottle, jinja2
>> pip install colorama colorlog docopt bottle jinja2

"""

import threading  # to run threads
from socketserver import ThreadingTCPServer  # socket server (with multi-threads capabilities)

from colorama import Fore
from docopt import docopt  # used to parse the command line
from importlib import import_module    # to dynamically import modules

from CGS.PlayerSocket import PlayerSocketHandler  # TCP socket handler for players
from CGS.Webserver import runWebServer  # to run the webserver (bottle)
from CGS.Game import Game
from CGS.Logger import configureRootLogger

usage = """
Coding Game Server
Run the servers (Game server and web server)

Usage:
  runCGS.py -h | --help
  runCGS.py <gameName> [options] [--debug|--dev|--prod]

Options:
  gameName                 Name of game [default: Labyrinth]
  -h --help                Show this screen.
  -p PORT --port=PORT      Game server port [default: 1234].
  -w PORT --web=PORT       Web server port [default: 8080].
  -H HOST --host=HOST      Servers host [default: localhost].
  -e EMAIL --email=EMAIL   Email address used in prod to send info when the server fails [default: pythoncgs@gmail.com]
  -s SMTP --smtp=SMTP      SMTP server:port used in prod to send the email [default: smtp.gmail.com:587]
  -l LOGS --log=LOGS       Folder where the logs are stored [default: logs/{{hostname}}/]
  --no-email               Do not send email in production [default: False]
  --debug                  Debug mode (log and display everything)
  --dev                    Development mode (log everything, display infos, warnings and errors)
  --prod                   Production mode (log only infos, warnings and errors, display nothing, and send emails) [default: True]
"""


if __name__ == "__main__":

	# parse the command line
	args = docopt(usage)
	if (not args['--debug']) and (not args['--dev']) and (not args['--prod']):
		args['--prod'] = True
	args['--port'] = int(args['--port'])
	args['--web'] = int(args['--web'])
	gameName = args['<gameName>']


	# import the <gameName> module and store it (in Game)
	try:
		mod = import_module(gameName + '.server.' + gameName)
		if gameName not in mod.__dict__:
			print(
					Fore.RED + "Error: The file `" + gameName + "/server/" + gameName
					+ ".py` must contain a class named `" + gameName + "`." + Fore.RESET
			)
			quit()
		Game.setTheGameClass(mod.__dict__[gameName])
	except ImportError as e:
		print(Fore.RED + "Error: Impossible to import the file `" + gameName + "/server/" + gameName + ".py`." + Fore.RESET)
		print(e)
		quit()

	# configure the loggers
	logger = configureRootLogger(args)

	# Start !
	mode = 'prod' if args['--prod'] else 'dev' if args['--dev'] else 'debug'
	logger.message("")
	logger.message("#=====================================================#")
	logger.message("# Coding Game Server is going to start (mode=`%s`) #" % mode)
	logger.message("#=====================================================#")
	logger.message("")

	# Run the webserver
	threading.Thread(
		target=runWebServer,
		kwargs={'host': args['--host'], 'port': args['--web'], 'quiet': True}
	).start()

	# TODO: remove this... Just for debug
	from CGS.Tournament import Tournament
	t = Tournament('toto', 12, 3, 'SingleEliminationTournament')

	# Start TCP Socket server (connection to players)
	PlayerServer = ThreadingTCPServer((args['--host'], args['--port']), PlayerSocketHandler)
	logger.message("Run the game server on port %d...", args['--port'])
	threading.Thread(target=PlayerServer.serve_forever())




# TODO: rajouter un timeout pour le dataReceive (il y a ça dans la classe BaseRequestHandler)
# TODO: mettre en forme les emails (qd ça vient du webserver)
# TODO: GameAPI.c rajouter le nom du joueur et de la partie dans les affichages de debug (utile qd on lance plusieurs joueurs sur sa machine)
