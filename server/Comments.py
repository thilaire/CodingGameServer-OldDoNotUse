"""
* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL

File: Comments.py
	ALl needed to deal with comments

Copyright 2016-2017 T. Hilaire, J. Brajard
"""

from collections import namedtuple
from colorama import Fore, Style

Comment = namedtuple('Comment', ['msg', 'owner', 'read'])


class CommentQueue:
	"""
	List of comments. Work as a queue, except that:
	- store comments from player0 and player1
	- only the last N comments of each player are stored
	- the 2N comments are stored ordered
	- we keep in mind those are read (by each player) and those aren't

	"""

	def __init__(self, N):
		"""

		Parameters:
		- N: (int) number of item per player
		"""
		self._comments = []
		self._N = N
		self._size = [0, 0]      # number of comments per player


	def append(self, msg, nPlayer):
		"""
		Append a comment
		Parameters:
		- msg: (string) comment to append
		- nPlayer: (int) who send the comment
		"""
		# add the new comment
		comment = Comment(msg, nPlayer, [False, False])  # unread message owned by nPlayer
		self._comments.append(comment)
		self._size[nPlayer] += 1

		# remove old one
		if self._size[nPlayer] > self._N:
			# iterator over all the comments owned by nPlayer
			own = (i for i, x in enumerate(self._comments) if x.owner == nPlayer)
			# remove the 1st one (the oldest)
			self._comments.pop(next(own))
			self._size[nPlayer] -= 1



	def getString(self, nPlayer, playerNames):
		"""
		Get the last comments not yet seen by player nPlayer (at least 2N)
		Parameters:
		- nPlayer: (int) number of the player who want the comments
		- playerNames: list of the name of the two players

		Returns a string (to send to the client)
		"""
		# FIXME: modify this so that it could also send last comments to websocket
		# get the list of unread comments
		comments = []

		for x in self._comments:
			if not x.read[nPlayer]:
				x.read[nPlayer] = True
				comments.append(Fore.WHITE + Style.BRIGHT + "[%s] %s" % (playerNames[x.owner], x.msg) + Fore.RESET + Style.NORMAL)

		return "\n".join(comments)

