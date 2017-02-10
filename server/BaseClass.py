"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev...

File: WebSocketBase.py
	Contains the base class to answer to websockets asking for information about the derived clas
	-> defines the generic behavior wrt websockets
	-> Game, RegularPlayer, Tournament will derived from it

"""

import logging
from geventwebsocket import WebSocketError
import json
from server.Logger import configureBaseClassLogger
logger = logging.getLogger()


class BaseClass:
	"""
	This class is the base class of the classes Player, Game and Tournament

	It put in common:
	- the dictionary of all the instances (all the players, all the games, etc.)
	- the name
	- the logger
	- some methods to manage the webSockets
	(send informations about objects and list of objects to webpages, through websockets)

	"""

	allInstances = {}          # unnecessary (will be overwritten by the inherited classe, and unused)
	_LoIWebSockets = []       # list of webSockets for the lists of Instance (LoI) informations

	# TODO: we should use weak references here (for the allInstances dictionary)
	# (see http://stackoverflow.com/questions/37232884/in-python-how-to-remove-an-object-from-a-list-if-it-is-only-referenced-in-that)

	def __init__(self, name):
		"""
		Base constructor
		- store the name, create the logger
		- add the object to the dictionary of all instances
		- and create list of websockets

		Should be called at the end of the subclass init

		Parameters:
		name: (string) name of the instance
		"""
		# store the name
		self._name = name

		# create and configure the logger
		self._logger = configureBaseClassLogger(self.__class__, name)

		# list of (instance) websocket
		self._lwsocks = []

		# add itself to the dictionary of games
		if name in self.allInstances:
			raise ValueError("A %s with the same name already exist" % self.__class__.__name__)
		self.allInstances[name] = self

		# send the new list of instances to web listeners
		self.sendListofInstances()



	# ===========
	# Properties
	# ===========
	@property
	def name(self):
		"""Returns the name of the object"""
		return self._name

	@property
	def logger(self):
		"""Returns the logger of the object"""
		return self._logger

	# ========================
	# Manage list of instances
	# ========================

	@classmethod
	def getFromName(cls, name):
		"""
		Get an instance of this class from its name
		Parameters:
		- name: (string) name of the instance (used as key in the dictionary)

		Returns the object or None if it doesn't exist
		"""
		return cls.allInstances.get(name, None)


	@classmethod
	def removeInstance(cls, name):
		"""
		Remove one instance
		- remove from the dictionary of all the instances
		- close the logger handlers associated (close the log files)
		Parameters:
		- name: (string) name of the instance
		"""
		# remove from the list of instances
		if name in cls.allInstances:
			obj = cls.allInstances[name]
			# close the associated logger handlers (close file)
			for handler in obj.logger.handlers[:]:
				handler.close()
				obj.logger.removeHandler(handler)
			del cls.allInstances[name]
			cls.sendListofInstances()




	# ===================================
	# List of Instances (LoI) WebSockets
	# ===================================

	@staticmethod
	def registerLoIWebSocket(wsock):
		"""
		Register a List of Instance websocket
		-> this websocket will receive informations (list of all the instances) everytime these lists change
		Parameter:
		- wsock: (WebSocket) the websocket to register
		"""
		# add this websocket in the list of LoI websockets
		logger.low_debug("register List of instances")
		BaseClass._LoIWebSockets.append(wsock)


	@staticmethod
	def removeLoIWebSocket(wsock):
		"""
		Remove this websocket (the socket has closed)
		Parameter:
		- wsock: (WebSocket) the websocket to remove
 		"""
		logger.low_debug("remove list of instances websocket")
		try:
			BaseClass._LoIWebSockets.remove(wsock)
		except ValueError:
			logger.low_debug("Remove a LoI WebSocket that do not exist !!")



	@staticmethod
	def sendListofInstances(wsock=None):
		"""
		Send list of instances through all the websockets (or only one if given)
		Called everytime the list of instances is changed
		Parameters:
		- wsock: (websocket) if None, the data is sent to all the websockets, otherwise only to this one
		"""
		d = {cls.__name__: [obj.HTMLrepr() for obj in cls.allInstances.values()] for cls in BaseClass.__subclasses__()}
		js = json.dumps(d)
		logger.low_debug("send List of instances : {%s}" % (d.keys(),))
		# send to all the websockets or only to one
		lws = BaseClass._LoIWebSockets if wsock is None else [wsock]
		for ws in lws:
			try:
				ws.send(js)
			except WebSocketError:
				logger.low_debug("WebSocketError in sendListInstances")
				BaseClass.removeLoIWebSocket(ws)


	# ===================
	# Instance Websockets
	# ===================
	def registerWebSocket(self, wsock):
		"""
		Register a websocket
		-> this websocket will receive informations (json dictionary) everytime this object has changed
		Parameter:
		- wsock: (WebSocket) the websocket to register
		"""
		# add this websocket in the list of  websockets
		logger.low_debug("register (instance) websocket")
		self._lwsocks.append(wsock)


	def removeWebSocket(self, wsock):
		"""
		Remove this websocket (the socket has closed)
		Parameter:
		- wsock: (WebSocket) the websocket to remove
 		"""
		logger.low_debug("remove (instance) websocket")
		try:
			self._lwsocks.remove(wsock)
		except ValueError:
			logger.low_debug("Remove a WebSocket that do not exist !!")


	def sendUpdateToWebSocket(self, wsock=None):
		"""
		Send some informations about self through all the websockets (or only one, if wsock is specified)
		Called everytime the object (self) is changed
		Parameters:
		- wsock: (websocket) if None, the data is sent to all the websockets, otherwise only to this one
		"""
		js = json.dumps(self.getDictInformations())
		logger.low_debug("send information to webseocket")
		# send to all the websockets or only to one
		lws = self._lwsocks if wsock is None else [wsock]
		for ws in lws:
			try:
				ws.send(js)
			except WebSocketError:
				logger.low_debug("WebSocketError in sendUpdateToWebSocket")
				self.removeWebSocket(ws)


	def getDictInformations(self):
		"""
		Send information (a dictionary) about the object

		TO BE OVERLOADED

		"""
		return {}

