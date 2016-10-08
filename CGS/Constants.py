"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev... (not even a beta)

File: Constants.py
	Contains the constants and config parameters used in the games

"""


TIMEOUT_TURN = 100		    # time (in seconds) to play a move


# return codes
# 0 is ok
# >0 for a winning move
# <0 for an illegal move
MOVE_OK = 0
MOVE_WIN = 1
MOVE_LOSE = -1       # TODO: find a better constant name

# Formating string indicating  the length of the message
SIZE_FMT = "%04d"
