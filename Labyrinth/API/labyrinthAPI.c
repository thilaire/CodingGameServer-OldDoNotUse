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
    ConnectToCGS( serverName, port, name);
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
    closeCGSConnection();
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
	waitForGame( labyrinthName, data);

	/* parse the data */
	sscanf( data, "%d %d", sizeX, sizeY);

	/* store the sizes, so that we can reuse them during getLabyrinth */
	nX = *sizeX;
	nY = *sizeY;
}

/* ---------> STOP HERE <-------------- */

/* -------------------------------------
 * Get the labyrinth and tell who starts
 * It fills the char* data with the data of the labyrinth
 * 1 if there's a wall, 0 for nothing
 *
 * Parameters:
 * - data: the array of date (the pointer data MUST HAVE allocated with the right size !!
 *
 * Returns 0 if you begin, or 1 if the opponent begins
 */
int getLabyrinth( char* data)
{
	sendString( __FUNCTION__,"GET_GAME_DATA");

	/* read Labyrinth name */
	bzero(buffer,1000);
	int r = read(sockfd, buffer, 255);
	if (r<0)
		dispError( __FUNCTION__, "Cannot read answer from 'GET_GAME_DATA' command (sending:%s)");

	dispDebug(__FUNCTION__, "Receive labyrinth's data:%s", buffer);

	/* copy the data in the array lab
	 * the buffer is a readable string of char '0' and '1'
	 * */
	char *p = buffer;
	for( int i=0; i<nX*nY; i++)
		*data++ = *p++ - '0';

	/* read if we begin (0) or if the opponent begins (1) */
	bzero(buffer,1000);
	r = read(sockfd, buffer, 255);
	if (r<0)
		dispError( __FUNCTION__, "Cannot read answer from 'GET_GAME_DATA' command (sending:%s)");

	dispDebug(__FUNCTION__, "Receive these player who begins=%s", buffer);

	return buffer[0]-'0';
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
	int result;
	sendString( __FUNCTION__, "GET_MOVE");

	/* read move */
	bzero(buffer,1000);
	int r = read(sockfd, buffer, 255);
	if (r<0)
		dispError( __FUNCTION__, "Cannot read answer from 'GET_MOVE' command (sending:%s)");
	dispDebug(__FUNCTION__, "Receive that move:%s", buffer);

	/* extract move */
	sscanf( buffer, "%d%d", &(move->type), &(move->value));

	/* read the return code*/
	bzero(buffer,1000);
	r = read(sockfd, buffer, 255);
	if (r<0)
		dispError( __FUNCTION__, "Cannot read answer from 'GET_MOVE' command (sending:%s)");
	dispDebug(__FUNCTION__, "Receive that return code:%s", buffer);

	/* extract result */
	sscanf( buffer, "%d", &result);

	return result;
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
	int result;
	sendString( __FUNCTION__, "PLAY_MOVE %d %d", move.type, move.value);


	/* read return code */
	bzero(buffer,1000);
	int r = read(sockfd, buffer, 255);
	if (r<0)
		dispError( __FUNCTION__, "Cannot read answer from 'PLAY_MOVE' command (sending:%s)");

	dispDebug(__FUNCTION__, "Receive that return code: %s", buffer);

	/* extract result */
	sscanf( buffer, "%d", &result);

	/* read the associated message */
	bzero(buffer,1000);
	r = read(sockfd, buffer, 255);
	if (r<0)
		dispError( __FUNCTION__, "Cannot read answer from 'PLAY_MOVE' command (sending:%s)");

	dispDebug(__FUNCTION__, "Receive that message: %s", buffer);

	/*TODO: that message is not handle or given to the user.. Todo ? */

	return result;
}



/* ----------------------
 * Display the labyrinth
 * in a pretty way (ask the server what to print)
 */
void printLabyrinth()
{
	dispDebug(__FUNCTION__, "Try to get string to display labyrinth");

	/* send command */
	sendString( __FUNCTION__, "DISP_GAME");

	/* get string to print */
	char buffer[1000];
	int r = read(sockfd, buffer, 1000);
	if (r<0)
		dispError( __FUNCTION__, "Cannot read string from socket");

	/* print it */
	printf("%s",buffer);
}



/*
 * Send a comment to the server
 *
 * Parameters:
 * - comment: (string) comment to send to the server (max 100 char.)
 */
void sendComment(char* comment) {
	dispDebug(__FUNCTION__, "Try to send a comment");

	/* max 100. car */
	if (strlen(comment)>100)
		dispError( __FUNCTION__, "The Comment is more than 100 characters.");

	/* send command */
	sendString(__FUNCTION__, "SEND_COMMENT %s", comment);
}