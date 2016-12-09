//
// TEMPLATE 
//
//
// Permet de jouer un seul tour (en ne faisant rien s'il commence ou en 
// réceptionnant le coup de l'adversaire s'il ne commence pas) 
// et termine le jeu.
// Ce programme vous sert de base pour construire votre propre programme



#include <stdio.h>
#include <stdlib.h>
#include "labyrinthAPI.h"
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

	/* connection to the server */
	connectToServer( "pc4023.polytech.upmc.fr", 1234, "prog_template");
	
	
	/* wait for a game, and retrieve informations about it */
	waitForLabyrinth( "DO_NOTHING timeout=10", labName, &sizeX, &sizeY);
	labData = (char*) malloc( sizeX * sizeY );
	player = getLabyrinth( labData);
	
	
	
	/* display the labyrinth */
	printLabyrinth();
	
	if (player==1)	/* The opponent plays */
	  {
	    ret = getMove( &move);
	    //playMove( &lab, move);
	  }
	else
	  {
	    move.type = DO_NOTHING;
	    move.value = 0;
	    ret = sendMove(move);
	  }
	
	if ((player ==1 && ret == MOVE_WIN) || (player==0 && ret == MOVE_LOSE))
	  printf("I lose the game\n");
	
	/* we do not forget to free the allocated array */
	free(labData);
	
	
	/* end the connection, because we are polite */
	closeConnection();
	
	return EXIT_SUCCESS;
}

