"""
* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *


Authors: T. Hilaire, J. Brajard
Licence: GPL

File: Logger.py
	contain function to configure the different loggers

Copyright 2016-2017 T. Hilaire, J. Brajard
"""

import logging  # logging system
from logging.handlers import RotatingFileHandler, SMTPHandler
import getpass        # get password without printing it
from socket import gethostname      # get name of the machine
from email.utils import parseaddr   # parse email to validate it (can validate wrong emails)
from colorlog import ColoredFormatter  # logging with colors
from colorama import Fore
from os import makedirs, remove, listdir
from os.path import getmtime, getsize, join, splitext
from smtplib import SMTP, SMTPAuthenticationError
from operator import itemgetter
from threading import Lock
from jinja2 import Template


# Max File Size (in octets)
MAX_ACTIVITY_SIZE = 1e6     # 1Mo for the activity.log file
MAX_BASECLASS_SIZE = {'Game':  10e3, 'Player': 100e3, 'Tournament': 1e6}  # 10ko per game and player, 1Mo per tournament
MAX_BASECLASS_FOLDER = {'Game':  1e6, 'Player': 5e6, 'Tournament': 1e6}   # 5Mo per game, player and tournament folders


# logging levels (see 'Logging.md'), depending on the mode
LOW_DEBUG_LEVEL = 5
MESSAGE_LEVEL = 35
activity_level = {
	'prod': (MESSAGE_LEVEL, logging.WARNING, logging.ERROR),
	'dev': (logging.INFO, logging.DEBUG),
	'debug': (logging.DEBUG, LOW_DEBUG_LEVEL)}
error_level = {'prod': logging.ERROR, 'dev': MESSAGE_LEVEL, 'debug': MESSAGE_LEVEL}
baseclass_level = {'prod': logging.INFO, 'dev': logging.DEBUG, 'debug': LOW_DEBUG_LEVEL}


# dictionary of Lockes, used for removeOldestWithLock (to that removeOldestFilePlayer is only run once a time)
lockDict = {}


# global variables used as configuration variables
class Config:
	"""Simple class to store the configuration parameters"""
	mode = ''       # default mode, set by configureRootLogger
	logPath = ''    # path where to store the log
	webPort = ''    # port of the web server
	host = ''       # name of the host


# function used to log message at low_debug and message levels
def low_debug(self, msg, *args, **kws):
	"""Log LOW_DEBUG in the logger"""
	if self.isEnabledFor(LOW_DEBUG_LEVEL):
		self._log(LOW_DEBUG_LEVEL, msg, args, **kws)


def message(self, msg, *args, **kws):
	"""Log MESSAGE in the logger"""
	if self.isEnabledFor(MESSAGE_LEVEL):
		self._log(MESSAGE_LEVEL, msg, args, **kws)


def configureRootLogger(args):
	"""
	Configure the main logger
	Parameters:
	- args: (dictionary) args from the command line

	Returns the logger
	"""
	# store the configuration in Config (datat used elsewhere)
	gameName = args['<gameName>']
	Config.mode = 'prod' if args['--prod'] else 'dev' if args['--dev'] else 'debug'
	Config.logPath = join('games', gameName, Template(args['--log']).render(hostname=gethostname()))
	Config.webPort = args['--web']
	Config.host = args['--host']

	# add the LOW_DEBUG and MESSAGE logging levels
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
			"""Simple fallback to get the password, see getpass module"""
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




def removeOldestFiles(cls, path, maxSize):
	"""
	Remove some of the oldest log file in path,  if that folder's size is greater than maxSize

	Parameters:
	- cls: (class) class of the objets concerned (used to test if some objects still exist)
	- path: (string) path where to look for .log files
	- maxSize: (int) maximum size (in octets) of the folder

	Remark: it uses listdir, but can be based on scandir (Python 3.5+) for efficiency
	"""

	# while sum(f.stat().st_size for f in scandir(path)) > (MAX_SIZE):     # -> for Python 3.5 (fastest!)
	while sum(getsize(path+f) for f in listdir(path)) > maxSize:

		# build the list (iterator) of log files that are not yet used (not in cls.allInstances dictionary)
		# files = ((f.name, f.stat().st_mtime) for f in scandir(path) if '.log' in f.name)      # -> for Python 3.5 (fastest!)
		files = ((f, getmtime(path + f)) for f in listdir(path) if
		         '.log' in f and splitext(f)[0] not in cls.allInstances)
		# remove the oldest file
		try:
			oldest = min(files, key=itemgetter(1))[0]
		except ValueError:
			# the list is empty, nothing to remove...
			break
		logging.getLogger().info("Remove the file `%s`" % (path+oldest))
		remove(path+oldest)

	# FIXME: this is not efficient. It should be better to i) build the list of log files that can be removed
	# and ii) in a loop, remove the oldest while the size of the deleted files is lower than the excedent


def removeOldestWithLock(cls, path, maxSize):
	"""
	Remove some of the oldest log file in path (call removeOldestFiles)
	*BUT* only if nobody is doing it with the same path (use Lock for that purpose)
	# inspired by http://codereview.stackexchange.com/questions/42802/a-non-blocking-lock-decorator-in-python
	:param path:
	:param maxSize:
	:param cls:
	:return:
	"""
	# get the lock associated to the path (create it if it doesn't exist)
	if path not in lockDict:
		lockDict[path] = Lock()
	lock = lockDict[path]

	# check if the call of removeOldestFiles is locked (for a given path)
	if lock.acquire(False):
		try:
			removeOldestFiles(cls, path, maxSize)
		finally:
			lock.release()
	else:
		# else do nothing (since removeOldestFilePlayer is already ran by a thread for this path,
		#  then there is no need to run it in the same time, otherwise it will cause some problems)
		pass



def configureBaseClassLogger(cls, objName):
	"""
	Configure a logger for BaseClass object (game, player or tournament)
	Parameters:
	- obj: instance of BaseClass (instance of Game, Player, League, etc.)

	Returns the logger
	"""
	# get the name of the class, or its parents
	className = cls.__name__
	if className not in MAX_BASECLASS_FOLDER:
		className = cls.__base__.__name__

	# create the logger and the associated folder
	logger = logging.getLogger(className + '-' + objName)
	path = join(Config.logPath, className + 's/')     # add a 's' at the end (Game -> Games)
	makedirs(path, exist_ok=True)

	# remove the oldest log files until the folder weights more than MAX_BASECLASS_FOLDER octets
	removeOldestWithLock(cls, path, MAX_BASECLASS_FOLDER[className])

	# add an handler to write the log to a file (MAX_PLAYER_SIZE octets max) *if* it doesn't exist
	if not logger.handlers:

		file_handler = RotatingFileHandler(path + objName + '.log', mode='a',
		                                   maxBytes=MAX_BASECLASS_SIZE[className], backupCount=1)
		file_handler.setLevel(baseclass_level[Config.mode])
		file_formatter = logging.Formatter('%(asctime)s | %(message)s', "%m/%d %H:%M:%S")
		file_handler.setFormatter(file_formatter)
		logger.addHandler(file_handler)

	return logger
