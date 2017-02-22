/*

Here is the API you gave to the players

With that API, they can connect to the server, play move, display the game, send comments, etc.

*/


#ifndef __API_CLIENT_TEMPLATE__
#define __API_CLIENT_TEMPLATE__
#include "ret_type.h"



/* define here the type defining a move */

/* A move is defined by ...*/
typedef struct
{
    /* insert your code here */
} t_move;


/* -------------------------------------
 * Initialize connection with the server
 * Quit the program if the connection to the server
 * cannot be established
 *
 * Parameters:
 * - serverName: (string) address of the server
 *   (it could be "localhost" if the server is run in local,
 *   or "pc4521.polytech.upmc.fr" if the server runs there)
 * - port: (int) port number used for the connection
 * - name: (string) name of the bot : max 20 characters
 *         (checked by the server)
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


 /* ----------------------------------------------------------------
 * Wait for a Game, and retrieve its name and first data (typically, array sizes)
 *
 * Parameters:
 * - fct: name of the function that calls waitForGame (used for the logging)
 * - gameType: string (max 50 characters) type of the training player we want to play with (empty string for regular game)
 * - gameName: string (max 50 characters), corresponds to the game name
 * - data: string (max 128 characters), corresponds to the data
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
 * The following options are common to every training player:
 *   - 'timeout': allows an define the timeout when training (in seconds)
 *   - 'seed': allows to set the seed of the random generator
 *   - 'start': allows to set who starts ('0' or '1')
 */
void waitForTemplateGame( char* gameType, char* labyrinthName, ...);


/* -------------------------------------
 * Get the data and tell who starts
 *
 * Parameters:
 * - data: pointer to data to fill
 *   (the pointer data MUST HAVE allocated with the right size !!)
 *
 * Returns 0 if you begin, or 1 if the opponent begins
 */
int getTemplateGameData( ...);



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
t_return_code getMove( t_move* move );



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
t_return_code sendMove( t_move move );



/* ----------------------
 * Display the Game
 * in a pretty way (ask the server what to print)
 */
void printTemplateGame();



/* ----------------------------
 * Send a comment to the server
 *
 * Parameters:
 * - comment: (string) comment to send to the server (max 100 char.)
 */
void sendComment(char* comment);



#endif
