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

#define DEBUG

/* port number to the server */
#define PORTNO	1234




/* global variables about the connection
 * we use them just to hide all the connection details to the user
 * so no need to knwo about them, or give them when we use the functions of this API
*/
int sockfd = -1;	/* socket descriptor -1 when we are not yet connected */
char buffer[1000];	/* global buffer used to send message (global so that it is not allocated/desallocated for each message; useful?) */

char dispbuffer[1000];	/* global buffer used to display error message  */


/* Display Error message
 * Parameters:
 * fct: function where the error raises
 * msg: message to display
 * ...: extra parameters to give to printf...
*/
void dispError(const char* fct, const char* msg, ...)
{
	va_list args;
	va_start (args, msg);
	sprintf(dispbuffer,"\e[5m\e[31m\u2327\e[2m (%s):\e[0m ", fct);
	vsprintf(dispbuffer+strlen(dispbuffer), msg, args);
	va_end (args);
	perror(dispbuffer);
	exit(EXIT_FAILURE);
}

/* Display Debug message (only if DEBUG constant is defined)
 * Parameters:
 * fct: function where the error raises
 * msg: message to display
 * ...: extra parameters to give to printf...
*/
void dispDebug(const char* fct, const char* msg, ...)
{
#ifdef DEBUG
	printf("\e[35m\u26A0\e[0m (%s) ", fct);

	/* print the msg, using the varying number of parameters */
	va_list args;
	va_start (args, msg);
	vprintf(msg, args);
	va_end (args);

	printf("\n");
#endif
}


/* Write str in the socket and get acknowledgment
 * accept extra parameters to give to sprintf...
 *
 * Manage connection problems
 */
void sendString( const char* fct, const char* str, ...) {
	va_list args;
	va_start (args, str);
	vsprintf(buffer, str, args);

	/* check if the socket is open */
	if (sockfd<0)
		dispError( fct, "The connection to the server is not established. Call 'connectToServer' before !");

	/* send our message */
	int r = write(sockfd, buffer, strlen(buffer));
	if (r < 0)
		dispError( fct, "Cannot write to the socket (%s)",buffer);

	/* get acknowledgment */
	bzero(buffer,256);
	r = read(sockfd, buffer, 255);
	if (r<0)
		dispError( fct, "Cannot read acknowldegment from socket (sending:%s)", str);

	if (strcmp(buffer,"OK"))
		dispError( fct, "Server do not acknowledge (send:%s)",buffer);
}



/*
Initialize connection with the server
Parameters:
- serverName: (string) address of the server (it could be "localhost" if the server is run in local, or "pc4521.polytech.upmc.fr" if the server runs there)
 - name: (string) name of the bot

Quit the program if the connection to the server cannot be established
*/
void connectToServer( char* serverName, char* name)
{
	struct sockaddr_in serv_addr;
	struct hostent *server;

	dispDebug("connectToServer", "Try to connect");

	/* Create a socket point, TCP/IP protocol, connected */
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd < 0)
		dispError("connectToServer","Impossible to open socket");

	/* Get the server */
	server = gethostbyname(serverName);
	if (server == NULL)
		dispError("connectToServer","Unable to find the server by its name");

	/* Allocate sockaddr */
	bzero((char *) &serv_addr, sizeof(serv_addr));
	serv_addr.sin_family = AF_INET;
	bcopy((char *)server->h_addr, (char *)&serv_addr.sin_addr.s_addr, server->h_length);
	serv_addr.sin_port = htons(PORTNO);

	/* Now connect to the server */
	if (connect(sockfd, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0)
		dispError("connectToServer", "Connection to the server impossible (is the server up?)");


	/* Sending a request with our name */
	sendString( "connectToServer", "CLIENT_NAME: %s",name);

	dispDebug("connectToServer", "Succeeded");
}


/* close the connection
*/
void closeConnection()
{
	if (sockfd<0)
		dispError("closeConnection","The connection to the server is not established. Call 'connectToServer' before !");
	close(sockfd);
}



/* wait for a labyrinth, and retrieve its name and size
Parameters:
- labyrinthName: char* (max 20 characters), corresponds to the labyrinth name
- sizeX and sizeY: int*, size of the labyrinth */
void waitForLabyrinth( char* labyrinthName, int* sizeX, int* sizeY)
{
  sendString( __FUNCTION__,"WAIT_ROOM:");
  strcpy( labyrinthName, "FakeName");
  *sizeX = 10;
  *sizeY = 10;
}


#define END_OF_DATA	0
#define WALL		1
#define US			2
#define OPPONENT	3
#define TREASURE	4

/* retrieve the labyrinth datas,
	0 if there is no more data to retrieve
	1 for a wall
	2 for your position
	3 for the opponent
	4 for the treasure
*/
void retrieveData( int* type, int* x, int* y)
{
}


/* returns 0 if it's your turn, or 1 if it's the opponent's turn
Useful in the beginning, to know who starts
*/
int getWhoStarts()
{

}

/* get the move of the opponent / send our move
A move is a tuple (type,value):
- type can be ROTATE_LINE_UP, ROTATE_LINE_DOWN, ROTATE_COLUMN_UP, ROTATE_COLUMN_DOWN, MOVE_LEFT, MOVE_RIGHT, MOVE_UP or MOVE_DOWN
- in case of rotation, the value indicates the number of the line (or column) to be rotated
Returns 1 if the game is finished, 0 otherwise */
#define ROTATE_LINE_UP		0
#define ROTATE_LINE_DOWN	1
#define ROTATE_COLUMN_UP	2
#define ROTATE_COLUMN_DOWN	3
#define MOVE_UP				4
#define MOVE_DOWN			5
#define MOVE_LEFT			6
#define MOVE_RIGHT			7
int getMove( int* type, int* val)
{
}
int sendMove(int type, int val)
{
}

/* display the labyrinth */
void printLabyrinth()
{
	dispDebug("printLabyrinth", "Try to get string to display labyrinth");

	/* send command */
	sendString( "printLabyrinth", "DISP_LAB:");

	/* get string to print */
	char buffer[10000];
	int r = read(sockfd, buffer, 255);
	if (r<0)
		dispError( "printLabyrinth", "Cannot read string from socket");

	/* print it */
	printf("%s",buffer);
}

/* send a comment */
void sendComment(char* comment)
{
}
