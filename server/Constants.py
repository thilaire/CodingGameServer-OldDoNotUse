#coding: utf-8


"""
Some constants

"""
#TODO: set timeout to 7 seconds
TIMEOUT_TURN = 1000		    # time (in seconds) to play a move

# return codes
# 0 is ok
# >0 for a winning move
# <0 for an illegal move

MOVE_OK = 0
MOVE_WIN = 1
MOVE_LOSE = -1       #TODO: MOVE_ILLEGAL or MOVE_INVALID ??