/*
* ------------------------ *
|                          |
|   -= LabyrinthAPI =-     |
|                          |
* ------------------------ *


Authors: T. Hilaire, J. Brajard
Licence: GPL
Status: still in dev... (not even a beta)

File: labyrinthAPI.h
	Contains the client API for the Labyrinth game


*/


#ifndef __API_CLIENT_LABYRINTH__
#define __API_CLIENT_LABYRINTH__
#include "GameAPI.h"
/* TODO: enlever l'inclusion de GameAPI.h, puisque ce truc est interne... il faudra (je ne vois pas comment faire autrement) recopier le t_return_code ici... */
typedef enum
{
	ROTATE_LINE_LEFT = 	0,
	ROTATE_LINE_RIGHT = 1,
	ROTATE_COLUMN_UP = 2,
	ROTATE_COLUMN_DOWN = 3,
	MOVE_UP = 4,
	MOVE_DOWN = 5,
	MOVE_LEFT = 6,
	MOVE_RIGHT = 7,
	DO_NOTHING = 8
} t_typeMove;


/*
A move is a tuple (type,value):
- type can be ROTATE_LINE_LEFT, ROTATE_LINE_RIGHT, ROTATE_COLUMN_UP, ROTATE_COLUMN_DOWN, MOVE_LEFT, MOVE_RIGHT, MOVE_UP or MOVE_DOWN
- in case of rotation, the value indicates the number of the line (or column) to be rotated
*/
typedef struct
{
	t_typeMove type;		/* type of the move */
	int value;				/* value associated with the type (number of the line or the column to rotate) */
} t_move;




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
int getLabyrinth( char* lab);



/* ----------------------
 * Get the opponent move
 *
 * Parameters:
 * - move: a move
 *
 * Returns a return_code (0 for normal move, 1 for a winning move, -1 for a losing (or illegal) move)
 * this code is relative to the opponent (+1 if HE wins, ...)
 */
t_return_code getMove( t_move* move );



/* -----------
 * Send a move
 *
 * Parameters:
 * - move: a move
 *
 * Returns a return_code (0 for normal move, 1 for a winning move, -1 for a losing (or illegal) move
 */
t_return_code sendMove( t_move move );



/* ----------------------
 * Display the labyrinth
 * in a pretty way (ask the server what to print)
 */
void printLabyrinth();



/* ----------------------------
 * Send a comment to the server
 *
 * Parameters:
 * - comment: (string) comment to send to the server (max 100 char.)
 */
void sendComment(char* comment);



#endif
