/* MANUAL_PLAY
Basic file to play the game and get a feel of the different possible moves.

Allows you to get the board data then enter the endless loop,
and loop while nobody made a wrong move.
*/

#include <stdio.h>
#include <stdlib.h>
#include <networksAPI.h>
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
	char Name[20];
	sprintf(Name,"prog_%d",getpid());

	/* connection to the server */
	connectToServer("localhost", 1234, Name);
	
	/* wait for a game, and retrieve informations about it */
	//waitForBoard("DO_NOTHING timeout=10", boardName, &sizeX, &sizeY);
	waitForBoard("", boardName, &sizeX, &sizeY);
	boardData = (char*) malloc(sizeX * sizeY);
	player = getBoardData(boardData);
	
	while(ret == NORMAL_MOVE) {
		/* get new board and display it */
		sleep(1);
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
			scanf("%d %d %d", &move.type, &move.x, &move.y);
			printf("\n");
			ret = sendMove(move);
		}

		/* switch players */
		player = !player;
	}
	
	if ((player == 0 && ret == WINNING_MOVE) || (player == 1 && ret == LOOSING_MOVE))
		printf("I lose the game :(\n");
	else
		printf("I win the game :)\n");
	
	/* we do not forget to free the allocated array */
	free(boardData);
	
	/* end the connection, because we are polite */
	closeConnection();
	
	return EXIT_SUCCESS;
}

