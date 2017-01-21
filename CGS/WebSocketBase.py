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

	allInstances = {}          # unnecessary (will be overwritten by the inherited classe, and unused)
	_classWebSockets = []       # list of webSockets for class informations

	def __init__(self, name):
		"""
		Base constructor
		add the object to the dictionary of all instances
		and create list of websockets

		Parameters:
		name: (string) name of the instance
		"""

		#TODO: rajouter l'attribut dans la classe de base (au lieu de dans chaque classe héritée)

		# add itself to the dictionary of games
		self.allInstances[name] = self

		# send the new list of instances to web listeners
		self.sendListofInstances()


	@staticmethod
	def registerLoIWebSocket(wsock):
		logger.low_debug("register List of instances")
		WebSocketBase._classWebSockets.append(wsock)


	@staticmethod
	def removeLoIWebSocket(wsock):
		logger.low_debug("remove list of instances websocket")
		print("Remove wsock")
		pass
		# TODO: remove wsock


	@staticmethod
	def sendListofInstances():
		"""
		Send list of instances through all the websockets
		Called everytime the list of instances is changed
		"""
		d = {cls.__name__: [obj.HTMLrepr() for obj in cls.allInstances.values()] for cls in WebSocketBase.__subclasses__()}
		js = json.dumps(d)
		logger.low_debug("send List of instances : {%s}" % (d,))
		for ws in WebSocketBase._classWebSockets:
			try:
				ws.send(js)
			except WebSocketError:
				logger.low_debug("WebSocketError in sendListInstances")
		# TODO: enlever le ws qui fait une erreur


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
		# remove from the list of instances
		if name in cls.allInstances:
			del cls.allInstances[name]
			cls.sendListofInstances()



