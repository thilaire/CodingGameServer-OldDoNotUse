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

logger = logging.getLogger()


# TODO: renommer la WebSocketBase en qq chos qui ne fait pas forcément référence au WebSocket


class WebSocketBase:

	_allInstances = {}          # dictionary of all the instances
	_classWebSockets = []       # list of webSockets for class informations

	def __init__(self, name):
		"""
		Base constructor
		add the object to the dictionary of all instances
		and create list of websockets

		Parameters:
		name: (string) name of the instance
		"""

		# add itself to the dictionary of games
		self._allInstances[name] = self

		# send the new list of instances to web listeners
		self.__class__.sendListInstances()


	@classmethod
	def registerClassWebSocket(cls, wsock):
		logger.low_debug("register class WS for %s" % cls.__name__)
		cls._classWebSockets.append(wsock)


	@classmethod
	def removeClassWebSocket(cls, wsock):
		logger.low_debug("remove class WS for %s" % cls.__name__)
		print("Remove wsock")
		pass
		# TODO: remove wsock


	@classmethod
	def sendListInstances(cls):
		"""
		Send list of instances through all the websockets
		Called everytime the list of instances is changed
		"""
		d = {name: obj.HTMLrepr() for name, obj in cls._allInstances.items()}
		logger.low_debug("send List of instance for %s: {%s}" % (cls.__name__, d))
		for ws in cls._classWebSockets:
			try:
				ws.send(json.dumps(d))
			except WebSocketError:
				logger.low_debug("WebSocketError in sendListInstances for %s" % (cls.__name__, ))
		# TODO: enlever le ws qui fait une erreur


	@classmethod
	def getFromName(cls, name):
		"""
		Get an instance of this class from its name
		Parameters:
		- name: (string) name of the instance (used as key in the dictionary)

		Returns the object or None if it doesn't exist
		"""
		return cls._allInstances.get(name, None)


	def removeInstance(self, name):
		# remove from the list of instances
		del self._allInstances[name]
		self.sendListInstances()




