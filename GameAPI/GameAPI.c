/*

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

File: GameAPI.c
	Functions for the Game API (connexion to the Coding Game Server)

TODO: explain...

*/

#include <stdio.h>
#include <stdlib.h>

#include <netdb.h>
#include <netinet/in.h>

#include <string.h>
#include <unistd.h>
#include <stdarg.h>

#include "GameAPI.h"


/* global variables about the connection
 * we use them just to hide all the connection details to the user
 * so no need to know about them, or give them when we use the functions of this API
*/


int sockfd = -1;		/* socket descriptor, equal to -1 when we are not yet connected */
char buffer[1000];		/* global buffer used to send message (global so that it is not allocated/desallocated for each message; TODO: is it useful?) */
int debug=0;			/* debug constant; we do not use here a #DEFINE, since it allows the client to declare 'extern int debug;' set it to 1 to have debug information, without having to re-compile labyrinthAPI.c */


/* Display Error message and exit
 *
 * Parameters:
 * - fct: name of the function where the error raises (__FUNCTION__ can be used)
 * - msg: message to display
 * - ...: extra parameters to give to printf...
*/
void dispError(const char* fct, const char* msg, ...)
{
	va_list args;
	va_start (args, msg);
	fprintf( stderr, "\e[5m\e[31m\u2327\e[2m (%s)\e[0m ", fct);
	vfprintf( stderr, msg, args);
	fprintf( stderr, "\n");
	va_end (args);
	exit(EXIT_FAILURE);
}


/* Display Debug message (only if `debug` constant is set to 1)
 *
 * Parameters:
 * - fct: name of the function where the error raises (__FUNCTION__ can be used)
 * - msg: message to display
 * - ...: extra parameters to give to printf...
*/
void dispDebug(const char* fct, const char* msg, ...)
{
	if (debug)
	{
		printf("\e[35m\u26A0\e[0m (%s) ", fct);

		/* print the msg, using the varying number of parameters */
		va_list args;
		va_start (args, msg);
		vprintf(msg, args);
		va_end (args);

		printf("\n");
	}
}


/* Send a string through the open socket and get acknowledgment (OK)
 * Manage connection problems
 *
 * Parameters:
 * - fct: name of the function that calls sendString (used for the logging)
 * - str: string to send
 * - ...:  accept extra parameters for str (string expansion)
 */
void sendString( const char* fct, const char* str, ...) {
	va_list args;
	va_start (args, str);
	bzero(buffer,1000);
	vsprintf(buffer, str, args);

	/* check if the socket is open */
	if (sockfd<0)
		dispError( fct, "The connection to the server is not established. Call 'connectToServer' before !");

	/* send our message */
	int r = write(sockfd, buffer, strlen(buffer));
	dispDebug( fct, "Send '%s' to the server", buffer);
	if (r < 0)
		dispError( fct, "Cannot write to the socket (%s)",buffer);

		/* get acknowledgment */
	bzero(buffer,1000);
	r = read(sockfd, buffer, 255);
	if (r<0)
		dispError( fct, "Cannot read acknowledgment from socket (sending:%s)", str);

	if (strcmp(buffer,"OK"))
		dispError( fct, "Error: The server does not acknowledge, but answered: %s",buffer);

	dispDebug( fct, "Receive acknowledgment from the server");
}



/* -------------------------------------
 * Initialize connection with the server
 * Quit the program if the connection to the server cannot be established
 *
 * Parameters:
 * - fct: name of the function that calls connectToCGS (used for the logging)
 * - serverName: (string) address of the server (it could be "localhost" if the server is run in local, or "pc4521.polytech.upmc.fr" if the server runs there)
 * - port: (int) port number used for the connection	TODO: should we fix it ?
 * - name: (string) name of the bot : max 20 characters (checked by the server)
 */
void connectToCGS( const char* fct, char* serverName, int port, char* name)
{
	struct sockaddr_in serv_addr;
	struct hostent *server;

	dispDebug( fct, "Initiate connection with %s (port: %d)", serverName, port);

	/* Create a socket point, TCP/IP protocol, connected */
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd < 0)
		dispError( fct, "Impossible to open socket");

	/* Get the server */
	server = gethostbyname(serverName);
	if (server == NULL)
		dispError( fct, "Unable to find the server by its name");
	dispDebug( fct, "Open connection with the server %s", serverName);

	/* Allocate sockaddr */
	bzero((char *) &serv_addr, sizeof(serv_addr));
	serv_addr.sin_family = AF_INET;
	bcopy((char *)server->h_addr, (char *)&serv_addr.sin_addr.s_addr, server->h_length);
	serv_addr.sin_port = htons(port);

	/* Now connect to the server */
	if (connect(sockfd, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0)
		dispError( fct, "Connection to the server '%s' on port %d impossible.", serverName, port);

	/* Sending our name */
	sendString( fct, "CLIENT_NAME %s",name);
}


/* ----------------------------------
 * Close the connection to the server
 * to do, because we are polite
 *
 * Parameters:
 * - fct: name of the function that calls closeCGSConnection (used for the logging)
*/
void closeCGSConnection( const char* fct)
{
	if (sockfd<0)
		dispError( fct,"The connection to the server is not established. Call 'connectToServer' before !");
	close(sockfd);
}



/* ------------------------------------------------------------------------------
 * Wait for a Game, and retrieve its name and first data (typically, array sizes)
 *
 * Parameters:
 * - fct: name of the function that calls waitForGame (used for the logging)
 * - gameName: string (max 50 characters), corresponds to the game name
 * - data: string (max 128 characters), corresponds to the data
 */
void waitForGame( const char* fct, char* gameName, char* data)
{
	sendString( fct,"WAIT_GAME");

	/* read Labyrinth name */
	bzero(buffer,1000);
	int r = read(sockfd, buffer, 255);
	if (r<0)
		dispError( fct, "Cannot read answer from 'WAIT_GAME' command (sending:%s)");

	dispDebug(fct, "Receive Labyrinth name=%s", buffer);
	strcpy( gameName, buffer);

	/* read Labyrinth size */
	bzero(buffer,1000);
	r = read(sockfd, buffer, 255);
	if (r<0)
		dispError( fct, "Cannot read answer from 'WAIT_GAME' command (sending:%s)");

	dispDebug( fct, "Receive Labyrinth sizes=%s", buffer);
	strcpy( data, buffer);
}



/* -------------------------------------
 * Get the game data and tell who starts
 * It fills the char* data with the data of the game (it will be parsed by the caller)
 * 1 if there's a wall, 0 for nothing
 *
 * Parameters:
 * - fct: name of the function that calls gameGetData (used for the logging)
 * - data: the array of game (the pointer data MUST HAVE allocated with the right size !!)
 *
 * Returns 0 if the client begins, or 1 if the opponent begins
 */
int getGameData( const char* fct, char* data)
{
	sendString( fct, "GET_GAME_DATA");

	/* read game data */
	int r = read(sockfd, data, 255);
	if (r<0)
		dispError( fct, "Cannot read answer from 'GET_GAME_DATA' command (sending:%s)");

	dispDebug( fct, "Receive labyrinth's data:%s", data);


    /* TODO: copier le buffer dans data
    pour cela, il faut peut-être connaitre la taille
    On passe d'abord la taille, ou bien c'est une taille fixe ???
    Julien, je te laisse régler ce pb ?*/


	/* read if we begin (0) or if the opponent begins (1) */
	bzero(buffer,1000);
	r = read(sockfd, buffer, 255);
	if (r<0)
		dispError( fct, "Cannot read answer from 'GET_GAME_DATA' command (sending:%s)");

	dispDebug( fct, "Receive these player who begins=%s", buffer);

	return buffer[0]-'0';
}



/* ----------------------
 * Get the opponent move
 *
 * Parameters:
 * - fct: name of the function that calls getCGSMove (used for the logging)
 * - move: a string representing a move (the caller will parse it to extract the move's values)
 *
 * Fill the move and returns a return_code (0 for normal move, 1 for a winning move, -1 for a losing (or illegal) move)
 * this code is relative to the opponent (+1 if HE wins, ...)
 */
t_return_code getCGSMove( const char* fct, char* move )
{
	int result;
	sendString( fct, "GET_MOVE");

	/* read move */
	int r = read(sockfd, move, 255);
	if (r<0)
		dispError( fct, "Cannot read answer from 'GET_MOVE' command (sending:%s)");
	dispDebug(__FUNCTION__, "Receive that move:%s", move);

	/* read the return code*/
	bzero(buffer,1000);
	r = read(sockfd, buffer, 255);
	if (r<0)
		dispError( fct, "Cannot read answer from 'GET_MOVE' command (sending:%s)");
	dispDebug(__FUNCTION__, "Receive that return code:%s", buffer);

	/* extract result */
	sscanf( buffer, "%d", &result);

	return result;
}



/* -----------
 * Send a move
 *
 * Parameters:
 * - fct: name of the function that calls sendCGSMove (used for the logging)
 * - move: a string representing a move (the caller will parse it to extract the move's values)
 *
 * Returns a return_code (0 for normal move, 1 for a winning move, -1 for a losing (or illegal) move
 */
t_return_code sendCGSMove( const char* fct, char* move)
{
	int result;
	sendString( fct, "PLAY_MOVE %s", move);


	/* read return code */
	bzero(buffer,1000);
	int r = read(sockfd, buffer, 255);
	if (r<0)
		dispError( fct, "Cannot read answer from 'PLAY_MOVE' command (sending:%s)");

	dispDebug( fct, "Receive that return code: %s", buffer);

	/* extract result */
	sscanf( buffer, "%d", &result);

	/* read the associated message */
	bzero(buffer,1000);
	r = read(sockfd, buffer, 255);
	if (r<0)
		dispError( fct, "Cannot read answer from 'PLAY_MOVE' command (sending:%s)");

	dispDebug( fct, "Receive that message: %s", buffer);

	/*TODO: that message is not handle or given to the user..

	 TH: À mon avis, il faut l'afficher que quand le résultat n'est pas MOVE_OK	 */

	return result;
}



/* ----------------------
 * Display the game
 * in a pretty way (ask the server what to print)
 *
 * Parameters:
 * - fct: name of the function that calls sendCGSMove (used for the logging)
 */
void printGame( const char* fct)
{
	dispDebug( fct, "Try to get string to display Game");

	/* send command */
	sendString( fct, "DISP_GAME");

	/* get string to print */
	char buffer[1000];
	int r = read(sockfd, buffer, 1000);
	if (r<0)
		dispError( fct, "Cannot read string from socket");

	/* print it */
	printf("%s",buffer);
}



/* ----------------------------
 * Send a comment to the server
 *
 * Parameters:
 * - fct: name of the function that calls sendCGSMove (used for the logging)
 * - comment: (string) comment to send to the server (max 100 char.)
 */
void sendCGSComment( const char* fct, char* comment)
{
	dispDebug( fct, "Try to send a comment");

	/* max 100. car */
	if (strlen(comment)>100)
		dispError( fct, "The Comment is more than 100 characters.");

	/* send command */
	sendString( fct, "SEND_COMMENT %s", comment);
}