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
Adaptation: 2017 M. Pecheux
"""

# chance to pop an asteroid while creating the board
ASTEROID_POP_CHANCE = 0.18

# constants defining a move
MOVE_UP = 0
MOVE_DOWN = 1
SHOOT = 2
ASTEROID_PUSH = 3
DO_NOTHING = 4

# simple dictionary of y offsets
Ddy = {MOVE_UP: -1, MOVE_DOWN: 1}

INITIAL_ENERGY = 100
SHOOT_ENERGY = 5
ASTEROID_PUSH_ENERGY = 15
