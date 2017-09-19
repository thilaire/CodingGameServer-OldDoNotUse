/* TEMPLATE
Basic file to adapt to make your own program.

Allows you to get the board data and play one turn.
*/

#include <stdio.h>
#include <stdlib.h>
#include "starshipsAPI.h"
#include <unistd.h>


extern int debug;	/* hack to enable debug messages */


int main()
{
	debug = 1;
	char boardName[50];					/* name of the board */
	char* boardData;					/* data of the board */
	t_return_code ret = NORMAL_MOVE;	/* indicates the status of the previous move */
	t_move move;						/* a move */
	int player;
	int sizeX, sizeY;

	/* connection to the server */
	connectToServer("localhost", 1234, "prog_template");
	
	/* wait for a game, and retrieve informations about it */
	waitForBoard( "DO_NOTHING timeout=10", boardName, &sizeX, &sizeY);
	boardData = (char*) malloc(sizeX * sizeY);
	player = getBoardData(boardData);
	
	/* display the board */
	printBoard();
	
	/* opponent turn */
	if (player == 1)
	{
		ret = getMove(&move);
	}
	/* your turn */
	else
	{
		printf("Your move: ");
		scanf("%d %d", &move.type, &move.value);
		printf("\n");
		ret = sendMove(move);
	}
	
	if ((player == 1 && ret == WINNING_MOVE) || (player == 0 && ret == LOOSING_MOVE))
		printf("I lose the game :(\n");
	else
		printf("I win the game :)\n");
	
	/* we do not forget to free the allocated array */
	free(boardData);
	
	/* end the connection, because we are polite */
	closeConnection();
	
	return EXIT_SUCCESS;
}

