//
// Created by Julien Brajard et Thibault Hilaire 01/02/2017.
//

//Programme Do Nothing pouvant participer au tournoi



#include <stdio.h>
#include <stdlib.h>
#include "labyrinthAPI.h"
#include <unistd.h>


int main()
{
	char labName[50];					/* name of the labyrinth */
	char* labData;						/* data of the labyrinth */
	t_return_code ret = MOVE_OK;		/* indicates the status of the previous move */
	t_move move;						/* a move */
	int player;
	int sizeX,sizeY;

	/* connection to the server */
	char nom[50];
	sprintf(nom,"DoNothingProg_%d",getpid());
	connectToServer( "pc4002.polytech.upmc.fr", 1234, nom);


	/* play over and over...
	(this loop is not necessary if you only want to play one game, but will be useful for tournament)*/
	while (1)
	{

		/* wait for a game, and retrieve informations about it */
	  waitForLabyrinth("TOURNAMENT TopTournament",labName,&sizeX,&sizeY);
	  // waitForLabyrinth( "", labName, &sizeX, &sizeY);
		labData = (char*) malloc( sizeX * sizeY );
		player = getLabyrinth( labData);
	
		do {

			/* display the labyrinth */
			printLabyrinth();
			if (player==1)	/* The opponent plays */
			{
				ret = getMove( &move);
			
			}
			else
			{
				//.... choose what to play
			  move.type = DO_NOTHING ;
			  move.value = 0;
			
			  ret = sendMove(move);
				
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

