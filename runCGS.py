#!/usr/bin/env python3

"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *


Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev... (not even a beta)

File: runCGS.py
	Main file/entry for the Coding Game Server
	->

"""

import logging  # logging system
import threading  # to run threads
from logging.handlers import RotatingFileHandler
from os import makedirs
from socketserver import ThreadingTCPServer  # socket server (with multi-threads capabilities)

from colorama import Fore
from colorlog import ColoredFormatter  # logging with colors
from docopt import docopt  # used to parse the command line
from importlib import import_module    # to dynamically import modules

from CGS.PlayerSocket import PlayerSocketHandler  # TCP socket handler for players
from CGS.Webserver import runWebServer  # to run the webserver (bottle)
from CGS.Player import Player
from CGS.Game import Game

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
  --debug                  Debug mode (log and display everything).
  --dev                    Development mode (log everything, display infos, warnings and errors).
  --prod                   Production mode (log only infos, warnings and errors, display nothing).
"""




if __name__ == "__main__":

	# parse the command line
	args = docopt(usage)
	if (not args['--debug']) and (not args['--dev']) and (not args['--prod']):
		args['--dev'] = True
	args['--port'] = int(args['--port'])
	args['--web'] = int(args['--web'])
	gameName = args['<gameName>']
	Player.gameName = gameName

	# import the <gameName> module and store it (in Game)
	try:
		mod = import_module(gameName + '.server.' + gameName)
		if gameName not in mod.__dict__:
			print(
				Fore.RED + "Error: The file `" + gameName + "/server/" + gameName + ".py` must contain a class named `" + gameName + "`." + Fore.RESET)
			quit()
	except ImportError:
		print(Fore.RED + "Error: Impossible to import the file `" + gameName + "/server/" + gameName + ".py`." + Fore.RESET)
		quit()
	Game.setTheGameClass(mod.__dict__[gameName])

	# Create and setup the logger
	logger = logging.getLogger()
	logger.setLevel(logging.INFO if args['--prod'] else logging.DEBUG)
	# add an handler to redirect the log to a file (1Mo max)
	makedirs(gameName+'/logs/', exist_ok=True)
	file_handler = RotatingFileHandler(gameName+'/logs/activity.log', 'a', 1000000, 1)
	file_handler.setLevel(logging.INFO if args['--prod'] else logging.DEBUG)
	file_formatter = logging.Formatter('%(asctime)s [%(name)s] | %(message)s', "%m/%d %H:%M:%S")
	file_handler.setFormatter(file_formatter)
	logger.addHandler(file_handler)
	# Add an other handler to redirect some logs to the console
	# (with colors, depending on the level DEBUG/INFO/WARNING/ERROR/CRITICAL)
	steam_handler = logging.StreamHandler()
	steam_handler.setLevel(logging.DEBUG if args['--debug'] else logging.INFO if args['--dev'] else logging.CRITICAL)
	LOGFORMAT = "  %(log_color)s[%(name)s]%(reset)s | %(log_color)s%(message)s%(reset)s"
	formatter = ColoredFormatter(LOGFORMAT)
	steam_handler.setFormatter(formatter)
	logger.addHandler(steam_handler)

	# Start !
	logger.info("#======================================#")
	logger.info("# Coding Game Server is going to start #")
	logger.info("#======================================#")

	# Run the webserver
	threading.Thread(
		target=runWebServer,
		kwargs={'host': args['--host'], 'port': args['--web'], 'quiet': True}
	).start()


	# Start TCP Socket server (connection to players)
	PlayerServer = ThreadingTCPServer((args['--host'], args['--port']), PlayerSocketHandler)
	logger.info("Run the game server on port %d...", args['--port'])
	threading.Thread(target=PlayerServer.serve_forever())


#TODO: (thib) rajouter un joueur DO_NOTHING, et tout le mécanisme nécessaire (dans WAIT_GAME)
#TODO: (julien) compléter dans play_move les actions du jeu (ROTATE_xxx), ajouter les points (pour les déplacements)
#TODO: gérer les comments (les mettre dans les listes des players, puis les ressortir à chaque DISP_GAME); pas plus de x comments entre deux tours, sinon on perd !
#TODO: (thib) logguer les déplacements

