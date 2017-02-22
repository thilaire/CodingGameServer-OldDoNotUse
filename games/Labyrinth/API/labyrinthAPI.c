/*
* ------------------------ *
|                          |
|   -= LabyrinthAPI =-     |
|                          |
| based on                 |
| Coding Game Server       |
|                          |
* ------------------------ *


Authors: T. Hilaire, J. Brajard
Licence: GPL

File: labyrinthAPI.c
	Contains the client API for the Labyrinth game
	-> based on clientAPI.c

Copyright 2016-2017 T. Hilaire, J. Brajard
*/


#include "clientAPI.h"
#include <stdio.h>
#include "labyrinthAPI.h"

unsigned char nX, nY; 	/* store lab size, used for getLabyrinth (the user do not have to pass them once again */


/* -------------------------------------
 * Initialize connection with the server
 * Quit the program if the connection to the server cannot be established
 *
 * Parameters:
 * - serverName: (string) address of the server (it could be "localhost" if the server is run in local, or "pc4521.polytech.upmc.fr" if the server runs there)
 * - port: (int) port number used for the connection
 * - name: (string) name of the player : max 20 characters (checked by the server)
 */
void connectToServer( char* serverName, int port, char* name)
{
	connectToCGS( __FUNCTION__, serverName, port, name);
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
	closeCGSConnection( __FUNCTION__ );
}



/* ----------------------------------------------------------------
 * Wait for a Labyrinth, and retrieve its name and its size
 *
 * Parameters:
 * - gameType: string (max 50 characters) type of the game
 *              we want to play
 *             (empty string for regular game)
 * - labyrinthName: string (max 50 characters),
 *                  corresponds to the game name
 * - sizeX, sizeY: sizes of the labyrinth
 *
 * gameType is a string like
 * "[TOURNAMENT <name> | TRAINING <name>] {options}"
 * where:
 * - {options} is in form "key1=value1 key2=value2 ..."
 * - <name> is the name of the tournament or the name of the training player
 * so the following message are accepted:
 *   - "WAIT_GAME {options}": wait for a regular game (with options)
 *   - "WAIT_GAME TOURNAMENT <name> {options}": register in the tournament <name> and wait for a game
 *   - "WAIT_GAME TRAINING <name> {options}": play agains a training player
 *
 * The options is composed by "key=value" pairs (invalid keys are ignored, invalid values leads to error)
 * The following options are common to every training player (when NAME is not empty or not TOURNAMENT):
 *   - 'timeout': allows an define the timeout when training (in seconds)
 *   - 'seed': allows to set the seed of the random generator
 *   - 'start': allows to set who starts ('0' or '1')
 * For training player, the <name> could be:
 * - "DO_NOTHING" to play against DO_NOTHING player (player that does not move)
 * - "PLAY_RANDOM" for a player that make random (legal) moves (option "rotate=False/True")
 * - "ASTAR" for a player that move the shortest way to the treasure
 *   (without making any rotation)
 */
void waitForLabyrinth( char* gameType, char* labyrinthName, int* sizeX, int* sizeY)
{
	char data[128];
	/* wait for a game */
	waitForGame( __FUNCTION__, training, labyrinthName, data);

	/* parse the data */
	sscanf( data, "%d %d", sizeX, sizeY);

	/* store the sizes, so that we can reuse them during getLabyrinth */
	nX = *sizeX;
	nY = *sizeY;
}



/* -------------------------------------
 * Get the labyrinth and tell who starts
 * It fills the char* lab with the data of the labyrinth
 * 1 if there's a wall, 0 for nothing
 *
 * Parameters:
 * - lab: the array of labyrinth (the pointer data MUST HAVE allocated with the right size !!
 *
 * Returns 0 if you begin, or 1 if the opponent begins
 */
int getLabyrinth( char* lab)
{
	char data[4096];
	/* wait for a game */
	int ret = getGameData( __FUNCTION__, data, 4096);

	/* copy the data in the array lab
	 * the datas is a readable string of char '0' and '1'
	 * */
	char *p = data;
	for( int i=0; i<nX*nY; i++)
		*lab++ = *p++ - '0';

    return ret;
}



/* ----------------------
 * Get the opponent move
 *
 * Parameters:
 * - move: a move
 *
 * Returns a return_code (0 for normal move, 1 for a winning move, -1 for a losing (or illegal) move)
 * this code is relative to the opponent (+1 if HE wins, ...)
 */
t_return_code getMove( t_move *move)
{

    char data[128];

    /* get the move */
    int ret = getCGSMove( __FUNCTION__, data,128);

	/* extract move */
	sscanf( data, "%d %d", &(move->type), &(move->value));
	dispDebug(__FUNCTION__,2,"move type:%d, ret:%d",move->type,ret);
	return ret;
}



/* -----------
 * Send a move
 *
 * Parameters:
 * - move: a move
 *
 * Returns a return_code (0 for normal move, 1 for a winning move, -1 for a losing (or illegal) move
 */
t_return_code sendMove( t_move move)
{
    /* build the string move */
    char data[128];
    sprintf( data, "%d %d", move.type, move.value);
// dispDebug(__FUNCTION__,"move send : %s",data);
    /* send the move */
	return sendCGSMove( __FUNCTION__, data);
}



/* ----------------------
 * Display the labyrinth
 * in a pretty way (ask the server what to print)
 */
void printLabyrinth()
{
    printGame( __FUNCTION__ );
}



/* -----------------------------
 * Send a comment to the server
 *
 * Parameters:
 * - comment: (string) comment to send to the server (max 100 char.)
 */
void sendComment(char* comment)
{
    sendCGSComment( __FUNCTION__, comment);
}
