/*
* ------------------------ *
|                          |
|   -= LabyrinthAPI =-     |
|                          |
* ------------------------ *


Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev... (not even a beta)

File: labyrinthAPI.c
	Contains the client API for the Labyrinth game
	-> based on GameAPI.c

*/

#include "GameAPI.h"
#include <stdio.h>
#include "labyrinthAPI.h"

unsigned char nX, nY; 	/* store lab size, used for getLabyrinth (the user do not have to pass them once again */


/* -------------------------------------
 * Initialize connection with the server
 * Quit the program if the connection to the server cannot be established
 *
 * Parameters:
 * - serverName: (string) address of the server (it could be "localhost" if the server is run in local, or "pc4521.polytech.upmc.fr" if the server runs there)
 * - port: (int) port number used for the connection	TODO: should we fix it ?
 * - name: (string) name of the bot : max 20 characters (checked by the server)
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



/* ----------------------------------------------------
 * Wait for a labyrinth, and retrieve its name and size
 *
 * Parameters:
 * - labyrinthName: string (max 50 characters), corresponds to the labyrinth name
 * - sizeX, sizeY: sizes of the labyrinth
 */
void waitForLabyrinth( char* labyrinthName, int* sizeX, int* sizeY)
{
	char data[128];
	/* wait for a game */
	waitForGame( __FUNCTION__, labyrinthName, data);

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
	int ret = getGameData( __FUNCTION__, data);

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
    int ret = getCGSMove( __FUNCTION__, data);

	/* extract move */
	sscanf( data, "%d%d", &(move->type), &(move->value));

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
    sscanf( data, "%d %d", &(move.type), &(move.value));

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
