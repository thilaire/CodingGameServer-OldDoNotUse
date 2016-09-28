"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *


Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev... (not even a beta)

File: CGS.py
	Main file/entry for the Coding Game Server
	-> import a class inheriting from Game
	-> and just call runCGS() !!

"""

import threading  # to run threads
from socketserver import ThreadingTCPServer  # socket server (with multi-threads capabilities)
from PlayerSocket import PlayerSocketHandler  # TCP socket handler for players
from Webserver import runWebserver  # to run the webserver (bottle)

import logging  # logging system
from logging.handlers import RotatingFileHandler
from colorlog import ColoredFormatter  # logging with colors
from docopt import docopt  # used to parse the command line


def runCGS():

	# parse the command line
	usage = """
Coding Game Server
Run the servers (Game server and web server)

Usage:
  runXXX.py -h | --help
  runXXX.py [options] [--debug|--dev|--prod]

Options:
  -h --help                Show this screen.
  -p PORT --port=PORT      Game server port [default: 1234].
  -w PORT --web=PORT       Web server port [default: 8080].
  -H HOST --host=HOST      Servers host [default: localhost].
  --debug                  Debug mode (log and display everything).
  --dev                    Development mode (log everything, display infos, warnings and errors).
  --prod                   Production mode (log only infos, warnings and errors, display nothing).
"""
	args = docopt(usage)
	if (not args['--debug']) and (not args['--dev']) and (not args['--prod']):
		args['--dev'] = True
	args['--port'] = int(args['--port'])
	args['--web'] = int(args['--web'])

	# Create and setup the logger
	# see http://sametmax.com/ecrire-des-logs-en-python/
	logger = logging.getLogger()
	logger.setLevel(logging.INFO if args['--prod'] else logging.DEBUG)
	# add an handler to redirect the log to a file (1Mo max)
	# todo: vérifier que
	file_handler = RotatingFileHandler('logs/activity.log', 'a', 1000000, 1)
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
	# TODO: is it necessary to use thread here, since bottle relies on paste server that is multi-threads ??
	threading.Thread(
		target=runWebserver,
		kwargs={'host': args['--host'], 'port': args['--web'], 'quiet': True}
	).start()

	# Start TCP Socket server (connection to players)
	PlayerServer = ThreadingTCPServer((args['--host'], args['--port']), PlayerSocketHandler)
	logger.info("Run the game server on port %d...", args['--port'])
	threading.Thread(target=PlayerServer.serve_forever())
