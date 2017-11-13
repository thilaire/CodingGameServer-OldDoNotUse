/*
* ------------------------ *
|                          |
|    -= NetworksAPI =-     |
|                          |
| based on                 |
| Coding Game Server       |
|                          |
* ------------------------ *


Authors: M. Pecheux (based on T. Hilaire and J. Brajard template file)
Licence: GPL

File: networksAPI.c
	Contains the client API for the Networks game
	-> based on clientAPI.c

Copyright 2017 M. Pecheux
*/


#include <clientAPI.h>
#include <stdio.h>
#include <networksAPI.h>

unsigned char nX, nY; 	/* store board size, used for getBoardData (the user do not have to pass them once again) */


/* -------------------------------------
 * Initialize connection with the server
 * Quit the program if the connection to the server cannot be established
 *
 * Parameters:
 * - serverName: (string) address of the server (it could be "localhost" if the server is run in local, or "pc4521.polytech.upmc.fr" if the server runs there)
 * - port: (int) port number used for the connection
 * - name: (string) name of the player : max 20 characters (checked by the server)
 */
void connectToServer(char* serverName, int port, char* name)
{
	connectToCGS(__FUNCTION__, serverName, port, name);
}


/* ----------------------------------
 * Close the connection to the server
 * to do, because we are polite
 *
 * Parameters:
 * None
*/
void closeConnection()
{
	closeCGSConnection(__FUNCTION__);
}


/* ----------------------------------------------------------------
 * Wait for a Grid, and retrieve its name and first data
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
void waitForBoard(char* training, char* boardName, int* sizeX, int* sizeY)
{
	char data[128];
	/* wait for a game */
	waitForGame(__FUNCTION__, training, boardName, data);

	/* parse the data */
	sscanf(data, "%d %d", sizeX, sizeY);

	/* store the sizes, so that we can reuse them during getBoardData */
	nX = *sizeX;
	nY = *sizeY;
}


/* -------------------------------------
 * Get the data and tell who starts
 *
 * Parameters:
 * - data: pointer to data to fill
 *   (the pointer data MUST HAVE allocated with the right size !!)
 *
 * Returns 0 if you begin, or 1 if the opponent begins
 */
int getBoardData(char* board)
{
	char data[4096];
	/* wait for a game */
	int ret = getGameData(__FUNCTION__, data, 4096);

	/* copy the data in the array board
	 * the datas is a readable string of char-able integers
	 * */
	char *p = data;
	for(int i = 0; i < nX*nY; i++)
		*board++ = *p++ - '0';

    return ret;
}



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
t_return_code getMove(t_move* move)
{
    char data[128];

    /* get the move */
    int ret = getCGSMove(__FUNCTION__, data, 128);

	/* extract move */
	sscanf(data, "%d %d %d", &(move->type), &(move->x), &(move->y));

	return ret;
}



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
t_return_code sendMove(t_move move)
{
    /* build the string move */
    char data[128];
    sprintf(data, "%d %d %d", move.type, move.x, move.y);

    /* send the move */
	return sendCGSMove(__FUNCTION__, data);
}




/* ----------------------
 * Display the Game board
 * in a pretty way (ask the server what to print)
 */
void printBoard()
{
    printGame(__FUNCTION__);
}



/* ----------------------------
 * Send a comment to the server
 *
 * Parameters:
 * - comment: (string) comment to send to the server (max 100 char.)
 */
void sendComment(char* comment)
{
    sendCGSComment(__FUNCTION__, comment);
}
