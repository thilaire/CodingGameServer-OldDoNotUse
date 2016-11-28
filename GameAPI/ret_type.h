/*
File : ret_type.h
Return type to be used both in general API and in
particular API (e.g. Labyrinth)
*/

#ifndef __RET_TYPE__
#define __RET_TYPE__

typedef enum
{
	MOVE_OK = 0,
	MOVE_WIN = 1,
	MOVE_LOSE = -1
} t_return_code;
#endif
