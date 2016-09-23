#coding: utf8



from socketserver import ThreadingTCPServer						# socket server (with multi-threads capabilities)
import threading												# to run threads
from bottle import run, request, response, install			# webserver (bottle)
import logging													# logging system
from logging.handlers import RotatingFileHandler
from colorlog import ColoredFormatter							# logging with colors
from docopt import docopt										# used to parse the command line
from functools import wraps										# use to wrap a logger for bottle

from Player import Player   #TODO: remove, used only for 'toto*' players
from socketPlayer import PlayerSocketHandler
import webserver												# import all the routes of the webserver


# parse the command line
usage = """
Labyrinth Game
Run the servers (Game server and web server)

Usage:
  server.py -h | --help
  server.py [options] [--debug|--dev|--prod]

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
if args['--debug'] == args['--dev'] == args['--prod'] == False:
	args['--dev'] = True
args['--port'] = int(args['--port'])
args['--web'] = int(args['--web'])


# setup the logger
# see http://sametmax.com/ecrire-des-logs-en-python/
# create and set up the logger
logger = logging.getLogger()
logger.setLevel( logging.INFO if args['--prod'] else logging.DEBUG )
# add an handler to redirect the log to a file (1Mo max)
file_handler = RotatingFileHandler('logs/activity.log', 'a', 1000000, 1)
file_handler.setLevel( logging.INFO if args['--prod'] else logging.DEBUG )
file_formatter = logging.Formatter( '%(asctime)s [%(name)s] | %(message)s',"%m/%d %H:%M:%S")
file_handler.setFormatter( file_formatter )
logger.addHandler(file_handler)
# add an other handler to redirect some logs to the console (with colors, depending on the level DEBUG/INFO/WARNING/ERROR/CRITICAL)
steam_handler = logging.StreamHandler()
steam_handler.setLevel( logging.DEBUG if args['--debug'] else logging.INFO if args['--dev'] else logging.CRITICAL )
LOGFORMAT = "  %(log_color)s[%(name)s]%(reset)s | %(log_color)s%(message)s%(reset)s"
formatter = ColoredFormatter(LOGFORMAT)
steam_handler.setFormatter( formatter)
logger.addHandler(steam_handler)


# add a logger wrapper for bottle (in order to log its activity)
# See http://stackoverflow.com/questions/31080214/python-bottle-always-logs-to-console-no-logging-to-file
weblogger = logging.getLogger('bottle')
def log_to_logger(fn):
	"""	Wrap a Bottle request so that a log line is emitted after it's handled."""
	@wraps(fn)
	def _log_to_logger(*_args, **_kwargs ):
		actual_response = fn(*_args, **_kwargs)
		weblogger.info('%s %s %s %s' % (request.remote_addr, request.method, request.url, response.status))
		return actual_response
	return _log_to_logger



# start
logger.info("#=========================================#")
logger.info("# Labyrinth Game server is going to start #")
logger.info("#=========================================#")


#DEBUG
#TODO: remove them
p1=Player("toto1")
p2=Player("toto2")



# Start the web server
#TODO: is it necessary to use thread here, since bottle relies on paste server that is multi-threads ??
threading.Thread(target=run, kwargs={  'host':args['--host'], 'port':args['--web'], 'quiet':True}).start()
#run( host=args['--host'], port=args['--web'], quiet=True)
install(log_to_logger)
weblogger.info( "Run the web server on port %d...", args['--web'])


# Start TCP Socket server (connection to players)
PlayerServer = ThreadingTCPServer( (args['--host'], args['--port']), PlayerSocketHandler)
logger.info( "Run the game server on port %d...", args['--port'])
threading.Thread( target=PlayerServer.serve_forever() )


