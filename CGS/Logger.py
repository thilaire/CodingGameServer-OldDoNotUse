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
from os import makedirs, scandir, remove, listdir
from os.path import getmtime, getsize
from smtplib import SMTP, SMTPAuthenticationError
from operator import itemgetter
import functools
from threading import Lock


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

mode = 'prod'   # default mode, set by configureRootLogger



# decorator for synchronizing off a thread mutex
# see https://github.com/GrahamDumpleton/wrapt/blob/develop/blog/07-the-missing-synchronized-decorator.md
def synchronized(lock=None):
    def _decorator(wrapped):
        @functools.wraps(wrapped)
        def _wrapper(*args, **kwargs):
            with lock:
                return wrapped(*args, **kwargs)
        return _wrapper
    return _decorator




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
	global mode  # TODO: faire mieux que ça...
	mode = 'prod' if args['--prod'] else 'dev' if args['--dev'] else 'debug'

	# add the COMM_DEBUG and MESSAGE logging levels
	logging.addLevelName(LOW_DEBUG_LEVEL, "COM_DEBUG")
	logging.Logger.low_debug = low_debug
	logging.addLevelName(MESSAGE_LEVEL, "MESSAGE")
	logging.Logger.message = message

	# Create and setup the logger
	logger = logging.getLogger()
	logger.setLevel(LOW_DEBUG_LEVEL)

	# add an handler to redirect the log to a file (1Mo max)
	makedirs(gameName + '/logs/', exist_ok=True)
	file_handler = RotatingFileHandler(gameName + '/logs/activity.log', mode='a', maxBytes=MAX_ACTIVITY_SIZE, backupCount=1)
	file_handler.setLevel(activity_level[mode][1])
	file_formatter = logging.Formatter('%(asctime)s [%(name)s] | %(message)s', "%m/%d %H:%M:%S")
	file_handler.setFormatter(file_formatter)
	logger.addHandler(file_handler)

	# Add an other handler to redirect some logs to the console
	# (with colors, depending on the level DEBUG/INFO/WARNING/ERROR/CRITICAL)
	steam_handler = logging.StreamHandler()
	steam_handler.setLevel(activity_level[mode][0])
	LOGFORMAT = "  %(log_color)s[%(name)s]%(reset)s | %(log_color)s%(message)s%(reset)s"
	formatter = ColoredFormatter(LOGFORMAT)
	steam_handler.setFormatter(formatter)
	logger.addHandler(steam_handler)

	# Manage errors (send an email) when we are in production
	if mode == 'prod' and False:        # TODO: enlever le False qd on saura passer le proxy
		# get the password (and disable warning message)
		# see http://stackoverflow.com/questions/35408728/catch-warning-in-python-2-7-without-stopping-part-of-progam
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
		mail_handler.setLevel(activity_level[mode][2])
		# mail_formatter = logging.Formatter('%(asctime)s [%(name)s] | %(message)s', "%m/%d %H:%M:%S")
		# mail_handler.setFormatter(mail_formatter)
		logger.addHandler(mail_handler)

	return logger


lockPlayer = Lock()
# TODO: do something more efficient than adding a mutex around configurePlayerLogger (the same for configureGameLogger)
@synchronized(lockPlayer)
def configurePlayerLogger(playerName, gameType):
	"""
	Configure a player logger
	Parameters:
	- playerName: (string) name of the player

	Returns the logger
	"""
	logger = logging.getLogger(playerName)
	path = gameType + '/logs/players/'

	# remove the oldest log files until the folder weights more than MAX_PLAYERS_FOLDER octets
	#while sum(f.stat().st_size for f in scandir(path)) > (MAX_PLAYERS_FOLDER-MAX_PLAYER_SIZE):     # -> for Python 3.5 (fastest!)
	while sum(getsize(path+f) for f in listdir(path)) > (MAX_PLAYERS_FOLDER - MAX_PLAYER_SIZE):
		#files = ((f.name, f.stat().st_mtime) for f in scandir(path) if '.log' in f.name)      # -> for Python 3.5 (fastest!)
		files = ((f, getmtime(path + f)) for f in listdir(path) if '.log' in f)
		# TODO: vérfier que le joueur que l'on supprime ne soit pas encore un train de jouer...(n'est plus dans Player.allPlayers)
		# sinon, il ne sera plus loggué
		# si on rajoute la condition dans l'itérateur, il faut un try/except pour le cas où la séquence est vide
		# (renvoie un ValueError)
		oldest = min(files, key=itemgetter(1))[0]
		logging.getLogger('DEL').warning("Remove the file `%s`" % (path+oldest))
		remove(path+oldest)

	# add an handler to write the log to a file (MAX_PLAYER_SIZE octets max) *if* it doesn't exist
	if not logger.handlers:
		makedirs(path, exist_ok=True)
		file_handler = RotatingFileHandler(path + playerName + '.log', mode='a', maxBytes=MAX_PLAYER_SIZE, backupCount=1)
		file_handler.setLevel(player_level[mode])
		file_formatter = logging.Formatter('%(asctime)s | %(message)s', "%m/%d %H:%M:%S")
		file_handler.setFormatter(file_formatter)
		logger.addHandler(file_handler)

	return logger



lockGame = Lock()

@synchronized(lockGame)
def configureGameLogger(name, gameType):
	"""
	Configure a game logger
	Parameters:
	- name: (string) name of the game
	- type: (string) type of the game (ex: 'Labyrinth')

	Returns the logger
	"""
	logger = logging.getLogger(name)
	path = gameType + '/logs/games/'

	# remove the oldest log files until the folder weights more than MAX_PLAYERS_FOLDER octets
	#while sum(f.stat().st_size for f in scandir(path)) > (MAX_GAMES_FOLDER-MAX_GAME_SIZE):     # -> for Python 3.5
	while sum(getsize(path + f) for f in listdir(path)) > (MAX_GAMES_FOLDER-MAX_GAME_SIZE):
		# files = ((f.name, f.stat().st_mtime) for f in scandir(path) if '.log' in f.name)      # -> for Python 3.5 (fastest!)
		files = ((f, getmtime(path + f)) for f in listdir(path) if '.log' in f)
		# TODO: vérfier que la partie que l'on supprime est bien terminée...(n'est plus dans Game.allGames)
		# si on rajoute la condition dans l'itérateur, il faut un try/except pour le cas où la séquence est vide
		# (renvoie un ValueError)
		oldest = min(files, key=itemgetter(1))[0]
		logging.getLogger().info("Remove the file `%s`" % (path+oldest))
		remove(path+oldest)

	# add an handler to write the log to a file (MAX_GAME_SIZE max) *if* it doesn't exist
	makedirs(path, exist_ok=True)
	file_handler = RotatingFileHandler(path + name + '.log', mode='a', maxBytes=MAX_GAME_SIZE, backupCount=1)
	file_handler.setLevel(game_level[mode])
	file_formatter = logging.Formatter('%(asctime)s | %(message)s', "%m/%d %H:%M:%S")
	file_handler.setFormatter(file_formatter)
	logger.addHandler(file_handler)

	return logger


