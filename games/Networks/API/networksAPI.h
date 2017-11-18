/*
* ------------------------ *
|                          |
|    -= NetworksAPI =-     |
|                          |
| based on                 |
| Coding Game Server       |
|                          |
* ------------------------ *


Authors: M. Pecheux
Licence: GPL

File: networksAPI.h
	Contains the client API for the Networks game
	-> based on clientAPI.h

Copyright 2017 M. Pecheux
*/


#ifndef __API_CLIENT_NETWORKS__
#define __API_CLIENT_NETWORKS__
//#include "../../../clientAPI/C/ret_type.h"
#include <ret_type.h>
typedef enum
{
	CAPTURE = 0,
	DESTROY = 1,
	LINK_H = 2,
	LINK_V = 3,
	DO_NOTHING = 4
} t_typeMove;


/*
A move is a tuple (type,value):
- type can be CAPTURE, DESTROY, LINK_H, LINK_V or DO_NOTHING
- in case of CAPTURE, the value indicates the coordinates
of the node to be captured
- in case of LINK_H, LINK_V or DESTROY the value indicates
the coordinates of link to be created or destroyed.
*/
typedef struct
{
	t_typeMove type; 	/* type of the move */
	int x; 				/* x-coordinate */
	int y; 				/* y-coordinate */
} t_move;


/* -------------------------------------
 * Initialize connection with the server
 * Quit the program if the connection to the server
 * cannot be established
 *
 * Parameters:
 * - serverName: (string) address of the server
 *   (it could be "localhost" if the server is run in local,
 *   or "pc4200.polytech.upmc.fr" if the server runs there)
 * - port: (int) port number used for the connection (e.g. 1234)
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


/* --------------------------------------------------------------
 * Wait for a Game, and retrieve its name and the size
 * of the board
 *
 * Parameters:
 * - training: string (max 50 characters)
 * - boardName: string (max 50 characters),
 *        corresponds to the game name
 * - sizeX, sizeY: sizes of the board
 *  Values poitned by boardName, sizeX and sizeY are initialized
 *  by the function call
 *
 * training is a string like "NAME key1=value1 key2=value1 ..."
 * - NAME can be empty. If not, It gives the type of
 *   the training player
 * - key=value pairs are used for options
 *   (each training player has its own options)
 *   invalid keys are ignored, invalid values leads to error
 *   the following keys are common to every training player
 *   (when NAME is not empty or not TOURNAMENT):
 *        - 'timeout': allows an define the timeout
 *                   when training (in seconds)
 *        - 'seed': allows to set the seed of the random generator
 *        - 'start': allows to set who starts ('0' or '1')
 * training could also be : "TOURNAMENT name" where name is the name of the tournament
 * to be joined by the bot
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
