"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL

File: Constants.py
	Contains the constants of the game Labyrinth
	-> defines the constants used for the client communication

Copyright 2016-2017 T. Hilaire, J. Brajard
"""


# constants defining a move
ROTATE_LINE_LEFT = 0
ROTATE_LINE_RIGHT = 1
ROTATE_COLUMN_UP = 2
ROTATE_COLUMN_DOWN = 3
MOVE_UP = 4
MOVE_DOWN = 5
MOVE_LEFT = 6
MOVE_RIGHT = 7
DO_NOTHING = 8

# simple dictionary of x and y offsets
Ddx = {MOVE_UP: 0, MOVE_DOWN: 0, MOVE_LEFT: -1, MOVE_RIGHT: 1}
Ddy = {MOVE_UP: -1, MOVE_DOWN: 1, MOVE_LEFT: 0, MOVE_RIGHT: 0}

INITIAL_ENERGY_FIRST = 0
INITIAL_ENERGY_SECOND = 2
ROTATE_ENERGY = 5

