"""

* --------------------- *
|                       |
|   Coding Game Server  |
|                       |
* --------------------- *

Authors: T. Hilaire, J. Brajard
Licence: GPL

File: Constants.py
	Contains the constants of the game Networks
	-> defines the constants used for the client communication

Copyright 2016-2017 T. Hilaire, J. Brajard
Adaptation: 2017 M. Pecheux
"""

# constants defining a move
CAPTURE = 0
DESTROY = 1
LINK_H = 2
LINK_V = 3
DO_NOTHING = 4

LINK_ENERGY = 5
DESTROY_ENERGY = 5

INITIAL_ENERGY_FIRST = 0
INITIAL_ENERGY_SECOND = 2

NODE_CODES_START_ID = 4
NODE_DISPLAY_CODES = [
	[u"\u25c7", u"\u25c6"],
	[u"\u25a1", u"\u25e9", u"\u25a0"],
	[u"\u25cb", u"\u25d4", u"\u25d1", u"\u25d5", u"\u25cf"],
]
NODE_TYPES = len(NODE_DISPLAY_CODES)
NODE_CODES_LENGTH = sum(map(len, NODE_DISPLAY_CODES))
MAX_NODES_COUNT = [-1, 5, 3]

# base codes are: 0-blank cell, 1-horizontal link, 2-vertical link, 3-goal node
# node codes (relative to start index, i.e. 0 = NODE_CODES_START_ID),
# are as follows:
'''
        |   NODE TYPE 1   |        NODE TYPE 2       |                 NODE TYPE 3                |
        |  St 1  |  St 2  |  St 1  |  St 2  |  St 3  |  St 1  |  St 2  |  St 3  |  St 4  |  St 5  |
---------------------------------------------------------------------------------------------------
Neutral |   =0   |   =1   |   =2   |   =3   |   =4   |   =5   |   =6   |   =7   |   =8   |   =9   |
        |    ◇   |    ◆   |    □   |    ◩   |    ■   |    ○   |    ◔   |    ◑   |    ◕   |    ●   |
---------------------------------------------------------------------------------------------------
Player1 |   =10  |   =11  |   =12  |   =13  |   =14  |   =15  |   =16  |   =17  |   =18  |   =19  |
(blue)  |    ◇   |    ◆   |    □   |    ◩   |    ■   |    ○   |    ◔   |    ◑   |    ◕   |    ●   |
---------------------------------------------------------------------------------------------------
Player2 |   =20  |   =21  |   =22  |   =23  |   =24  |   =25  |   =26  |   =27  |   =28  |   =29  |
(red)   |    ◇   |    ◆   |    □   |    ◩   |    ■   |    ○   |    ◔   |    ◑   |    ◕   |    ●   |
'''
