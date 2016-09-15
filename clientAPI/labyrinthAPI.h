#ifndef __API_CLIENT_LABYRINTH__
#define __API_CLIENT_LABYRINTH__

/*

#TODO: ...

*/




/* -------------------------------------
 * Initialize connection with the server
 * Quit the program if the connection to the server cannot be established
 *
 * Parameters:
 * - serverName: (string) address of the server (it could be "localhost" if the server is run in local, or "pc4521.polytech.upmc.fr" if the server runs there)
 * - port: (int) port number used for the connection
 * - name: (string) name of the bot : max 20 characters (checked by the server)
 */
void connectToServer( char* serverName, int port, char* name);



/* ----------------------------------
 * Close the connection to the server
 * to do, because we are polite
 *
 * Parameters:
 * None
*/
void closeConnection();



/* ----------------------------------------------------
 * Wait for a labyrinth, and retrieve its name and size
 *
 * Parameters:
 * - labyrinthName: string (max 50 characters), corresponds to the labyrinth name
 * - sizeX, sizeY: sizes of the labyrinth
 */
void waitForLabyrinth( char* labyrinthName, int* sizeX, int* sizeY);



/*
 * Get the labyrinth and tell who starts
 * It fills the char* data with the data of the labyrinth
 * 1 if there's a wall, 0 for nothing
 *
 * Parameters:
 * - data: the array of date (the pointer data MUST HAVE allocated with the right size !!
 *
 * Returns 0 if you begin, or 1 if the opponent begins
 */
int getLabyrinth( char* data);


/* get the move of the opponent / send our move
A move is a tuple (type,value):
- type can be ROTATE_LINE_LEFT, ROTATE_LINE_RIGHT, ROTATE_COLUMN_UP, ROTATE_COLUMN_DOWN, MOVE_LEFT, MOVE_RIGHT, MOVE_UP or MOVE_DOWN
- in case of rotation, the value indicates the number of the line (or column) to be rotated
Returns 1 if the game is finished, 0 otherwise */
#define ROTATE_LINE_LEFT	0
#define ROTATE_LINE_RIGHT	1
#define ROTATE_COLUMN_UP	2
#define ROTATE_COLUMN_DOWN	3
#define MOVE_UP				4
#define MOVE_DOWN			5
#define MOVE_LEFT			6
#define MOVE_RIGHT			7
#define DO_NOTHING			8

/*structure*/
int getMove( int* type, int* val);
int sendMove(int type, int val);

/* display the labyrinth */
void printLabyrinth();

/* send a comment, max 100 char. */
void sendComment(char* comment);



#endif