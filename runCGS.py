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

import logging  # logging system
from logging.handlers import RotatingFileHandler, SMTPHandler
import getpass        # get password without printing it
from socket import gethostname      # get name of the machine
from email.utils import parseaddr   # parse email to validate it (can validate wrong emails)

from os import makedirs

import threading  # to run threads
from socketserver import ThreadingTCPServer  # socket server (with multi-threads capabilities)

from colorama import Fore
from colorlog import ColoredFormatter  # logging with colors
from docopt import docopt  # used to parse the command line
from importlib import import_module    # to dynamically import modules

from CGS.PlayerSocket import PlayerSocketHandler  # TCP socket handler for players
from CGS.Webserver import runWebServer  # to run the webserver (bottle)
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
  -e EMAIL --email=EMAIL   Email address used in prod to send info when the server fails [default: pythoncgs@gmail.com]
  -s SMTP --smtp=SMTP      SMTP server:port used in prod to send the email [default: smtp.gmail.com:587]
  --debug                  Debug mode (log and display everything).
  --dev                    Development mode (log everything, display infos, warnings and errors).
  --prod                   Production mode (log only infos, warnings and errors, display nothing, and send emails).
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

	# Manage errors (send an email) when we are in production
	if args['--dev']:
		# get the password (and disable warning message)
		# see http://stackoverflow.com/questions/35408728/catch-warning-in-python-2-7-without-stopping-part-of-progam
		def custom_fallback(prompt="Password: ", stream=None):
			print("WARNING: Password input may be echoed (can not control echo on the terminal)")
			return getpass._raw_input(prompt)  # Use getpass' custom raw_input function for security
		getpass.fallback_getpass = custom_fallback  # Replace the getpass.fallback_getpass function with our equivalent
		password = getpass.getpass('Password for %s account:' % args['--email'])

		# check the smtp and address
		smtp,port = 0,''
		try:
			smtp, port = args['--smtp'].split(':')
			port = int(port)
		except ValueError:
			print(Fore.RED + "Error: The smtp is not valid (should be `smpt:port`)" + Fore.RESET)
			quit()
		address = parseaddr(args['--email'])[1]
		if not address:
			print(Fore.RED + "Error: The email address is not valid" + Fore.RESET)
			quit()
		# add an other handler to redirect errors through emails
		mail_handler = SMTPHandler(	(smtp, port), address, [address], "Error in CGS (%s)" % gethostname(), (address, password), secure=())
		#mail_handler = SMTPHandler( ("smtp.gmail.com", 587), 'pythoncgs@gmail.com', ['pythoncgs@gmail.com'], 'Error found', ('pythoncgs@gmail.com', 'Polytech'),secure=() )
		mail_handler.setLevel(logging.ERROR)
		#mail_formatter = logging.Formatter('%(asctime)s [%(name)s] | %(message)s', "%m/%d %H:%M:%S")
		#mail_handler.setFormatter(mail_formatter)
		logger.addHandler(mail_handler)


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




# TODO: gérer les comments (les mettre dans les listes des players, puis les ressortir à chaque DISP_GAME); pas plus de x comments entre deux tours, sinon on perd !
# TODO: (thib) revoir tous les niveaux des debug/infos/warning, etc.
# TODO: empêcher bottle (et playerServer) de garder les erreurs pour eux (il faut les logguer !!)
# TODO: rajouter un timeout pour le dataReceive (il y a ça dans la classe BaseRequestHandler)
# TODO: envoyer un email qd il y a une erreur
