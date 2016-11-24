//
// Created by Thib on 26/09/2016.
//

// Correspond à la question 1 (jouer à la main contre le serveur)



#include <stdio.h>
#include <stdlib.h>
#include "../API/labyrinthAPI.h"
#include <unistd.h>


extern int debug;	/* hack to enable debug messages */


int main()
{
	char labName[50];					/* name of the labyrinth */
	char* labData;						/* data of the labyrinth */
	t_return_code ret = MOVE_OK;		/* indicates the status of the previous move */
	t_move move;						/* a move */
	int player;
	int sizeX,sizeY;

	//debug=1;	/* enable debug */

	/* connection to the server */
	char nom[50];
	sprintf(nom,"ProgTest_%d",getpid());
	connectToServer( "localhost", 1234, nom);
	printf("Youhou, connecté au serveur !\n");


	/* play over and over...
	(this loop is not necessary if you only want to play one game, but will be useful for tournament)*/
	while (ret == MOVE_OK)
	{

		/* wait for a game, and retrieve informations about it */
		waitForLabyrinth( REGULAR_GAME, labName, &sizeX, &sizeY);
		labData = (char*) malloc( sizeX * sizeY );
		player = getLabyrinth( labData);

		do {

			/* display the labyrinth */
			printLabyrinth();

			if (player==1)	/* The opponent plays */
			{
				ret = getMove( &move);
				//playMove( &lab, move);
			}
			else
			{
				//.... choose what to play
				printf("\nIt's your turn to play (0:ROT_LEFT, 1:ROT_RIGHT, 2:ROT_UP, 3:ROT_DOWN, 4:UP, 5:DOWN, 6:LEFT, 7:RIGHT):");
				scanf("%d %d", &move.type, &move.value);
				printf("move: %d %d\n",move.type,move.value);
				ret = sendMove(move);
				//playMove( &lab, move);
			}

			/* change player */
			player = ! player;

		} while (ret==MOVE_OK);

		if ( (player==0 && ret==MOVE_WIN) || (player==1 && ret==MOVE_LOSE) )
			printf("\n Unfortunately, the opponent wins\n");
		else
			printf("\n Héhé, I win!!\n");

		/* we do not forget to free the allocated array */
		free(labData);
	}

	/* end the connection, because we are polite */
	closeConnection();

	return EXIT_SUCCESS;
}

