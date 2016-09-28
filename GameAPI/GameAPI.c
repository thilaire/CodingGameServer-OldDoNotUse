//
// Created by Thib on 20/06/2016.
//

#include <stdio.h>
#include <stdlib.h>

#include <netdb.h>
#include <netinet/in.h>

#include <string.h>
#include <unistd.h>
#include <stdarg.h>

#include "labyrinthAPI.h"


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
 * - serverName: (string) address of the server (it could be "localhost" if the server is run in local, or "pc4521.polytech.upmc.fr" if the server runs there)
 * - port: (int) port number used for the connection	TODO: should we fix it ?
 * - name: (string) name of the bot : max 20 characters (checked by the server)
 */
void connectToCGS( char* serverName, int port, char* name)
{
	struct sockaddr_in serv_addr;
	struct hostent *server;

	dispDebug( __FUNCTION__, "Initiate connection with %s (port: %d)", serverName, port);

	/* Create a socket point, TCP/IP protocol, connected */
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd < 0)
		dispError(__FUNCTION__,"Impossible to open socket");

	/* Get the server */
	server = gethostbyname(serverName);
	if (server == NULL)
		dispError(__FUNCTION__,"Unable to find the server by its name");
	dispDebug(__FUNCTION__, "Open connection with the server %s", serverName);

	/* Allocate sockaddr */
	bzero((char *) &serv_addr, sizeof(serv_addr));
	serv_addr.sin_family = AF_INET;
	bcopy((char *)server->h_addr, (char *)&serv_addr.sin_addr.s_addr, server->h_length);
	serv_addr.sin_port = htons(port);

	/* Now connect to the server */
	if (connect(sockfd, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0)
		dispError(__FUNCTION__, "Connection to the server '%s' on port %d impossible.", serverName, port);

	/* Sending our name */
	sendString( __FUNCTION__, "CLIENT_NAME %s",name);
}


/* ----------------------------------
 * Close the connection to the server
 * to do, because we are polite
 *
 * Parameters:
 * None
*/
void closeCGSConnection()
{
	if (sockfd<0)
		dispError(__FUNCTION__,"The connection to the server is not established. Call 'connectToServer' before !");
	close(sockfd);
}



/* ------------------------------------------------------------------------------
 * Wait for a Game, and retrieve its name and first data (typically, array sizes)
 *
 * Parameters:
 * - gameName: string (max 50 characters), corresponds to the game name
 * - data: string (max 128 characters), corresponds to the data
 */
void waitForGame( char* labyrinthName, char* data)
{
	sendString( __FUNCTION__,"WAIT_GAME");

	/* read Labyrinth name */
	bzero(buffer,1000);
	int r = read(sockfd, buffer, 255);
	if (r<0)
		dispError( __FUNCTION__, "Cannot read answer from 'WAIT_GAME' command (sending:%s)");

	dispDebug(__FUNCTION__, "Receive Labyrinth name=%s", buffer);
	strcpy( labyrinthName, buffer);

	/* read Labyrinth size */
	bzero(buffer,1000);
	r = read(sockfd, buffer, 255);
	if (r<0)
		dispError( __FUNCTION__, "Cannot read answer from 'WAIT_GAME' command (sending:%s)");

	dispDebug(__FUNCTION__, "Receive Labyrinth sizes=%s", buffer);
	strcpy( data, buffer);
}



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