#!/usr/bin/env python3

"""

* --------------------- *
|                       |
|   -= Labyrinth =-     |
|                       |
| based on the          |
|   Coding Game Server  |
|                       |
* --------------------- *


Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev... (not even a beta)

File: runLabyrinth.py
	Main file/entry for the Labyrinth Game Server
	-> run the Coding Game Server with the Labyrinth class

	see --help for args command

"""
import sys
sys.path.insert(0, '..')

from Labyrinth import Labyrinth
from CGS.CGS import runCGS

# Labyrinth class is not used here, but its importation makes the Coding Game Server knows that it should use it


runCGS(Labyrinth)
