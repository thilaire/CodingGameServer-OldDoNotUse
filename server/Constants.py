"""
* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL

File: Constants.py
	Contains the constants and config parameters used in the games

Copyright 2016-2017 T. Hilaire, J. Brajard
"""


TIMEOUT_TURN = 10		    # time (in seconds) to play a move


# return codes
# 0 is ok
# >0 for a winning move
# <0 for an illegal move
NORMAL_MOVE = 0
WINNING_MOVE = 1
LOSING_MOVE = -1

# Formatting string indicating  the length of the message
SIZE_FMT = "%04d"

# Maximum number of comments per player
MAX_COMMENTS = 5
