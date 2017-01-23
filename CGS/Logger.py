"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *


Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev...

File: Logger.py
	contain function to configure the different loggers
"""

import logging  # logging system
from logging.handlers import RotatingFileHandler, SMTPHandler
import getpass        # get password without printing it
from socket import gethostname      # get name of the machine
from email.utils import parseaddr   # parse email to validate it (can validate wrong emails)
from colorlog import ColoredFormatter  # logging with colors
from colorama import Fore
from os import makedirs, remove, listdir
from os.path import getmtime, getsize, join
from smtplib import SMTP, SMTPAuthenticationError
from operator import itemgetter
from functools import wraps
from threading import Lock
from jinja2 import Template

# Max File Size (in octets)
MAX_ACTIVITY_SIZE = 1e6     # 1Mo for the activity.log file
MAX_PLAYER_SIZE = 50e3       # 50ko each player
MAX_PLAYERS_FOLDER = 5e6     # 5Mo for the players/ folder
MAX_GAME_SIZE = 10e3         # 10ko each game
MAX_GAMES_FOLDER = 5e6       # 5Mo for the games/ folder


# see 'Logging.txt' for the different logging levels
LOW_DEBUG_LEVEL = 5
MESSAGE_LEVEL = 35
activity_level = {
	'prod': (MESSAGE_LEVEL, logging.WARNING, logging.ERROR),
	'dev': (logging.INFO, logging.DEBUG),
	'debug': (logging.DEBUG, LOW_DEBUG_LEVEL)}
player_level = {'prod': logging.INFO, 'dev': logging.DEBUG, 'debug': LOW_DEBUG_LEVEL}
game_level = {'prod': logging.INFO, 'dev': logging.DEBUG, 'debug': LOW_DEBUG_LEVEL}
error_level = {'prod': logging.ERROR, 'dev': MESSAGE_LEVEL, 'debug': MESSAGE_LEVEL}


# global variables used as configuration variables
class Config:
	mode = ''   # default mode, set by configureRootLogger
	logPath = ''   # path where to store the log
	webPort = ''    # port of the web server
	host = ''       # name of the host


# From http://codereview.stackexchange.com/questions/42802/a-non-blocking-lock-decorator-in-python
def non_blocking_lock(fn):
	"""Decorator. Prevents the function from being called multiple times simultaneously.
    If thread A is executing the function and thread B attempts to call the
    function, thread B will immediately receive a return value of None instead.
    """
	lock = Lock()

	@wraps(fn)
	def locker(*args, **kwargs):
		if lock.acquire(False):
			try:
				return fn(*args, **kwargs)
			finally:
				lock.release()

	return locker


# function used to log message at low_debug and message levels
def low_debug(self, msg, *args, **kws):
	if self.isEnabledFor(LOW_DEBUG_LEVEL):
		self._log(LOW_DEBUG_LEVEL, msg, args, **kws)


def message(self, msg, *args, **kws):
	if self.isEnabledFor(MESSAGE_LEVEL):
		self._log(MESSAGE_LEVEL, msg, args, **kws)


def configureRootLogger(args):
	"""
	Configure the main logger
	Parameters:
	- args: (dictionary) args from the command line

	Returns the logger
	"""
	gameName = args['<gameName>']
	Config.mode = 'prod' if args['--prod'] else 'dev' if args['--dev'] else 'debug'
	Config.logPath = join(gameName, Template(args['--log']).render(hostname=gethostname()))
	Config.webPort = args['--web']
	Config.host = args['--host']

	# add the COMM_DEBUG and MESSAGE logging levels
	logging.addLevelName(LOW_DEBUG_LEVEL, "COM_DEBUG")
	logging.Logger.low_debug = low_debug
	logging.addLevelName(MESSAGE_LEVEL, "MESSAGE")
	logging.Logger.message = message

	# Create and setup the logger
	logger = logging.getLogger()
	logger.setLevel(LOW_DEBUG_LEVEL)

	# add an handler to redirect the log to a file (1Mo max)
	makedirs(Config.logPath, exist_ok=True)
	file_handler = RotatingFileHandler(join(Config.logPath, 'activity.log'), mode='a',
	                                   maxBytes=MAX_ACTIVITY_SIZE, backupCount=1)
	file_handler.setLevel(activity_level[Config.mode][1])
	file_formatter = logging.Formatter('%(asctime)s [%(name)s] | %(message)s', "%m/%d %H:%M:%S")
	file_handler.setFormatter(file_formatter)
	logger.addHandler(file_handler)

	# Add an other handler to redirect some logs to the console
	# (with colors, depending on the level DEBUG/INFO/WARNING/ERROR/CRITICAL)
	steam_handler = logging.StreamHandler()
	steam_handler.setLevel(activity_level[Config.mode][0])
	LOGFORMAT = "  %(log_color)s[%(name)s]%(reset)s | %(log_color)s%(message)s%(reset)s"
	formatter = ColoredFormatter(LOGFORMAT)
	steam_handler.setFormatter(formatter)
	logger.addHandler(steam_handler)

	# An other handler to log the errors (only) in errors.log
	error_handler = RotatingFileHandler(join(Config.logPath, 'errors.log'), mode='a',
	                                    maxBytes=MAX_ACTIVITY_SIZE, backupCount=1)
	error_handler.setLevel(error_level[Config.mode])
	error_formatter = logging.Formatter('----------------------\n%(asctime)s [%(name)s] | %(message)s', "%m/%d %H:%M:%S")
	error_handler.setFormatter(error_formatter)
	logger.addHandler(error_handler)

	# Manage errors (send an email) when we are in production
	if Config.mode == 'prod' and not args['--no-email']:
		# get the password (and disable warning message)
		# see http://stackoverflow.com/questions/35408728/catch-warning-in-python-2-7-without-stopping-part-of-progam
		# noinspection PyUnusedLocal
		def custom_fallback(prompt="Password: ", stream=None):
			print("WARNING: Password input may be echoed (can not control echo on the terminal)")
			# noinspection PyProtectedMember
			return getpass._raw_input(prompt)  # Use getpass' custom raw_input function for security

		getpass.fallback_getpass = custom_fallback  # Replace the getpass.fallback_getpass function with our equivalent
		password = getpass.getpass('Password for %s account:' % args['--email'])
		# check the smtp and address
		smtp, port = 0, ''
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
		# check if the password/email/smtp works
		smtpserver = SMTP(smtp, port)
		smtpserver.ehlo()
		smtpserver.starttls()
		try:
			smtpserver.login(address, password)
		except SMTPAuthenticationError as err:
			print(Fore.RED + "Error: The email/smtp:port/password is not valid address is not valid (%s)" % err + Fore.RESET)
			quit()
		finally:
			smtpserver.close()

		# add an other handler to redirect errors through emails
		mail_handler = SMTPHandler((smtp, port), address, [address], "Error in CGS (%s)" % gethostname(),
		                           (address, password), secure=())
		mail_handler.setLevel(activity_level[Config.mode][2])
		# mail_formatter = logging.Formatter('%(asctime)s [%(name)s] | %(message)s', "%m/%d %H:%M:%S")
		# mail_handler.setFormatter(mail_formatter)
		logger.addHandler(mail_handler)

	return logger




def removeOldestFile(path, maxSize):
	"""
	Remove the oldest log file in path if the folder size is greater than MAX_SIZE
	Parameters:
	- path: (string) path where to look for .log files
	- maxSize: (int) maximum size (in octets) of the folder

	Use listdir, but can be based on scandir (Python 3.5+) for efficiency
	"""
	# while sum(f.stat().st_size for f in scandir(path)) > (MAX_SIZE):     # -> for Python 3.5 (fastest!)
	# TODO:  write a try..catch if path does not exist

	while sum(getsize(path+f) for f in listdir(path)) > maxSize:
		# files = ((f.name, f.stat().st_mtime) for f in scandir(path) if '.log' in f.name)      # -> for Python 3.5 (fastest!)
		files = ((f, getmtime(path + f)) for f in listdir(path) if '.log' in f)
		# TODO: vérfier que le joueur/game que l'on supprime ne soit pas encore un train de jouer...
		# (n'est plus dans Player.allPlayers / Games.allPGames)
		# sinon, il ne sera plus loggué
		# si on rajoute la condition dans l'itérateur, il faut un try/except pour le cas où la séquence est vide
		# (renvoie un ValueError)
		oldest = min(files, key=itemgetter(1))[0]
		logging.getLogger().info("Remove the file `%s`" % (path+oldest))
		remove(path+oldest)


# The two following functions just call removeOldestFile, but each with a different non-blocking lock
# so that these functions are just called when nobodyelse uses then
# (if removeOldestFilePlayer is already run by a thread, then no other thread can run it (do nothing instead)
# so that we do not have two functions that try to delete oldest files in the same time
# (one is enough; several causes troubles)
@non_blocking_lock
def removeOldestFilePlayer(path):
	return removeOldestFile(path, MAX_PLAYERS_FOLDER)


@non_blocking_lock
def removeOldestFileGame(path):
	return removeOldestFile(path, MAX_GAMES_FOLDER)


def configurePlayerLogger(playerName):
	"""
	Configure a player logger
	Parameters:
	- playerName: (string) name of the player

	Returns the logger
	"""
	logger = logging.getLogger(playerName)
	path = join(Config.logPath, 'players/')
	makedirs(path, exist_ok=True)

	# remove the oldest log files until the folder weights more than MAX_PLAYERS_FOLDER octets
	removeOldestFilePlayer(path)

	# add an handler to write the log to a file (MAX_PLAYER_SIZE octets max) *if* it doesn't exist
	if not logger.handlers:

		file_handler = RotatingFileHandler(path + playerName + '.log', mode='a', maxBytes=MAX_PLAYER_SIZE, backupCount=1)
		file_handler.setLevel(player_level[Config.mode])
		file_formatter = logging.Formatter('%(asctime)s | %(message)s', "%m/%d %H:%M:%S")
		file_handler.setFormatter(file_formatter)
		logger.addHandler(file_handler)

	return logger


def configureGameLogger(name):
	"""
	Configure a game logger
	Parameters:
	- name: (string) name of the game

	Returns the logger
	"""
	logger = logging.getLogger(name)
	path = join(Config.logPath, 'games/')
	makedirs(path, exist_ok=True)

	# remove the oldest log files until the folder weights more than MAX_PLAYERS_FOLDER octets
	removeOldestFileGame(path)

	# add an handler to write the log to a file (MAX_GAME_SIZE max) *if* it doesn't exist
	file_handler = RotatingFileHandler(path + name + '.log', mode='a', maxBytes=MAX_GAME_SIZE, backupCount=1)
	file_handler.setLevel(game_level[Config.mode])
	file_formatter = logging.Formatter('%(asctime)s | %(message)s', "%m/%d %H:%M:%S")
	file_handler.setFormatter(file_formatter)
	logger.addHandler(file_handler)

	return logger


