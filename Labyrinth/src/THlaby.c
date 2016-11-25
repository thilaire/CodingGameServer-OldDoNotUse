//
// Created by Thib on 26/09/2016.
//

// Pseudo A* pour jouer un minimum



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

//	debug=1;	/* enable debug */

	/* connection to the server */
	char nom[50];
	sprintf(nom,"ProgTest_%d",getpid());
	connectToServer( "localhost", 1234, nom);


	/* play over and over...
	(this loop is not necessary if you only want to play one game, but will be useful for tournament)*/
	while (ret == MOVE_OK)
	{

		/* wait for a game, and retrieve informations about it */
		waitForLabyrinth( "PLAY_RANDOM timeout=10 rotate=False", labName, &sizeX, &sizeY);
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
                move.type = DO_NOTHING;
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

