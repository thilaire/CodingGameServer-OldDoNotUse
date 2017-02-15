/*
* ------------------------------ *
|                                |
|   -= Coding Game Server =-     |
|                                |
|       client API in C          |
|                                |
* ------------------------------ *


Authors: T. Hilaire, J. Brajard
Licence: GPL

File: ret_type.h
	Return types to be used both in general API and in particular API (e.g. Labyrinth)

Copyright 2016-2017 T. Hilaire, J. Brajard
*/


#ifndef __RET_TYPE__
#define __RET_TYPE__

typedef enum
{
	NORMAL_MOVE = 0,
	WINNING_MOVE = 1,
	LOOSING_MOVE = -1
} t_return_code;

#endif
