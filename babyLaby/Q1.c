//
// Created by Thib on 26/09/2016.
//

// Correspond à la question 1 (jouer à la main contre le serveur)



#include <stdio.h>
#include <stdlib.h>
#include "../clientAPI/labyrinthAPI.h"
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

	debug=1;	/* enable debug */

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
		waitForLabyrinth( labName, &sizeX, &sizeY);
		labData = (char*) malloc( sizeX * sizeY );
		player = getLabyrinth( labData);

		printLabyrinth();

		do {
			if (player==1)	/* The opponent plays */
			{
				printf("\nOn attend le move"),
				ret = getMove( &move);
				printf("\nOn a reçu type=%d value%d ret=%d\n",move.type, move.value,ret);
				//playMove( &lab, move);
			}
			else
			{
				//.... choose what to play
				printf("\nIt's your turn to play (0:ROT_LEFT, 1:ROT_RIGHT, 2:ROT_UP, 3:ROT_DOWN, 4:UP, 5:DOWN, 6:LEFT, 7:RIGHT):");
				scanf("%d %d", &move.type, &move.value);
				ret = sendMove(move);
				printf("\nOn a reçuret=%d",ret);
				//playMove( &lab, type, val);
			}

			/* display the labyrinth */
			printLabyrinth();

			/* change player */
			player = ! player;

		} while (ret==MOVE_OK);


		/* we do not forget to free the allocated array */
		free(labData);
	}

	/* end the connection, because we are polite */
	closeConnection();

	return EXIT_SUCCESS;
}

