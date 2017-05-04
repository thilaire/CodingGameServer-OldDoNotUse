/*
* ------------------------ *
|                          |
|   -= StarshipsAPI =-     |
|                          |
| based on                 |
| Coding Game Server       |
|                          |
* ------------------------ *


Authors: M. Pecheux (based on T. Hilaire and J. Brajard template file)
Licence: GPL

File: starshipsAPI.h
	Contains the client API for the Starships game
	-> based on clientAPI.h

Copyright 2017 M. Pecheux
*/


#ifndef __API_CLIENT_STARSHIPS__
#define __API_CLIENT_STARSHIPS__
#include "../../../clientAPI/C/ret_type.h"

typedef enum
{
	MOVE_UP = 0,
	MOVE_DOWN = 1,
	SHOOT = 2,
	ASTEROID_PULL = 3,
	DO_NOTHING = 4
} t_typeMove;


/*
A move is a tuple (type,value):
- type can be MOVE_UP, MOVE_DOWN, SHOOT, PULL_ASTEROID or DO_NOTHING
- in case of SHOOT, the value indicates the number of energy cells to consume
(determines how many asteroids will be destroyed on the line)
- in case of PULL_ASTEROID, the value indicates the number of energy cells to consume
(determines how many cells the asteroid will be moved)
*/
typedef struct
{
	t_typeMove type; /* type of the move */
	int value; /* value associated with the type 
		      (number of energy cells to use)*/
} t_move;


/* -------------------------------------
 * Initialize connection with the server
 * Quit the program if the connection to the server
 * cannot be established
 *
 * Parameters:
 * - serverName: (string) address of the server
 *   (it could be "localhost" if the server is run in local,
 *   or "pc4521.polytech.upmc.fr" if the server runs there)
 * - port: (int) port number used for the connection
 * - name: (string) name of the bot : max 20 characters
 *         (checked by the server)
 */
void connectToServer(char* serverName, int port, char* name);



/* ----------------------------------
 * Close the connection to the server
 * to do, because we are polite
 *
 * Parameters:
 * None
*/
void closeConnection();


/* ----------------------------------------------------------------
 * Wait for a Game, and retrieve its name and first data
 * (typically, array sizes)
 *
 * Parameters:
 * - gameType: string (max 50 characters)
 * - boardName: string (max 50 characters),
 *                  corresponds to the game name
 * - sizeX, sizeY: sizes of the board
 *
 * gameType is a string like "NAME key1=value1 key2=value1 ..."
 * - NAME can be empty. It gives the type of the training player
 * - key=value pairs are used for options
 *   (each training player has its own options)
 *   invalid keys are ignored, invalid values leads to error
 *   the following options are common to every training player
 *   (when NAME is not empty or not TOURNAMENT):
 *        - 'timeout': allows an define the timeout
 *                   when training (in seconds)
 *        - 'seed': allows to set the seed of the random generator
 *        - 'start': allows to set who starts ('0' or '1')
 * gameType could also be : "TOURNAMENT name" where name is the name of the tournament
  */
void waitForBoard(char* training, char* boardName, int* sizeX, int* sizeY);


/* -------------------------------------
 * Get the data and tell who starts
 *
 * Parameters:
 * - data: pointer to data to fill
 *   (the pointer data MUST HAVE allocated with the right size !!)
 *
 * Returns 0 if you begin, or 1 if the opponent begins
 */
int getBoardData(char* board);



/* ----------------------
 * Get the opponent move
 *
 * Parameters:
 * - move: a move
 *
 * Returns a return_code
 * NORMAL_MOVE for normal move,
 * WINNING_MOVE for a winning move, -1
 * LOOSING_MOVE for a losing (or illegal) move
 * this code is relative to the opponent (WINNING_MOVE if HE wins, ...)
 */
t_return_code getMove(t_move* move);



/* -----------
 * Send a move
 *
 * Parameters:
 * - move: a move
 *
 * Returns a return_code
 * NORMAL_MOVE for normal move,
 * WINNING_MOVE for a winning move, -1
 * LOOSING_MOVE for a losing (or illegal) move
 * this code is relative to your programm (WINNING_MOVE if YOU win, ...)
 */
t_return_code sendMove(t_move move);



/* ----------------------
 * Display the Game
 * in a pretty way (ask the server what to print)
 */
void printBoard();



/* ----------------------------
 * Send a comment to the server
 *
 * Parameters:
 * - comment: (string) comment to send to the server (max 100 char.)
 */
void sendComment(char* comment);



#endif
