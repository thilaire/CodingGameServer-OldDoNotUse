/*
File : ret_type.h
Return type to be used both in general API and in
particular API (e.g. Labyrinth)
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
