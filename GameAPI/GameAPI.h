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

File: GameAPI.h
	Functions' prototypes for the Game API

TODO: explain...

*/



#ifndef __API_CLIENT_GAME__
#define __API_CLIENT_GAME__


/* Display Error message and exit
 *
 * Parameters:
 * - fct: name of the function where the error raises (__FUNCTION__ can be used)
 * - msg: message to display
 * - ...: extra parameters to give to printf...
*/
void dispError(const char* fct, const char* msg, ...);



/* Display Debug message (only if `debug` constant is set to 1)
 *
 * Parameters:
 * - fct: name of the function where the error raises (__FUNCTION__ can be used)
 * - msg: message to display
 * - ...: extra parameters to give to printf...
*/
void dispDebug(const char* fct, const char* msg, ...)



/* -------------------------------------
 * Initialize connection with the server
 * Quit the program if the connection to the server cannot be established
 *
 * Parameters:
 * - serverName: (string) address of the server (it could be "localhost" if the server is run in local, or "pc4521.polytech.upmc.fr" if the server runs there)
 * - port: (int) port number used for the connection
 * - name: (string) name of the bot : max 20 characters (checked by the server)
 */
void connectToCGS( char* serverName, int port, char* name);



/* ----------------------------------
 * Close the connection to the server
 * to do, because we are polite
 *
 * Parameters:
 * None
*/
void closeCGSConnection();



/* ------------------------------------------------------------------------------
 * Wait for a Game, and retrieve its name and first data (typically, array sizes)
 *
 * Parameters:
 * - gameName: string (max 50 characters), corresponds to the game name
 * - data: string (max 128 characters), corresponds to the data
 */
void waitForGame( char* labyrinthName, char* data);



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
int getLabyrinth( char* data);



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



/*
 * Send a comment to the server
 *
 * Parameters:
 * - comment: (string) comment to send to the server (max 100 char.)
 */
void sendComment(char* comment);



#endif