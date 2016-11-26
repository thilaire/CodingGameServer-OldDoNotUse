//
// Created by Thib on 26/09/2016.
//

// Pseudo A* pour jouer un minimum



#include <stdio.h>
#include <stdlib.h>
#include "../API/labyrinthAPI.h"
#include <unistd.h>


extern int debug;	/* hack to enable debug messages */

typedef struct {
	int sizeX,sizeY;	/* labyrinth size */
	char* data;			/* labyrinth data */
	int trX,trY;		/* treasure position */
	int X,Y;			/* our position */
	int opX,opY;		/* opponent position */
	int player;			/* gives who plays (0: us, 1: the opponent) */
} t_laby;


void waitLab( t_laby* lab, char* training)
{
	char labName[50];					/* name of the labyrinth  - don't care about it*/
	/* wait for labyrinth */
	waitForLabyrinth( training, labName, &(lab->sizeX), &(lab->sizeY));

	/* get the labyrinth */
	lab->data = (char*) malloc( lab->sizeX * lab->sizeY );
	lab->player = getLabyrinth( lab->data);

	/* initialize the positions */
	lab->trX = lab->sizeX/2;
	lab->trY = lab->sizeY/2;
    lab->opX = lab->player ? 0 : lab->sizeX - 1;
    lab->X = !lab->player ? 0 : lab->sizeX - 1;
	lab->opY = lab->sizeY/2;
	lab->Y = lab->sizeY/2;
}


/* rotate a line of the labyrinth */
void rotateLine( t_laby* lab, int line, int delta)
{
    printf("Not implemented yet!\n");
    exit(0);
}

/* rotate a column of the labyrinth */
void rotateColumn( t_laby* lab, int column, int delta)
{
    printf("Not implemented yet!\n");
}


/* Play a move (change the labyrinth and coordinate accordingly */
void playMove( t_laby* lab, t_move move)
{
	if (move.type==ROTATE_LINE_RIGHT)
		rotateLine(lab, move.value, 1);
	else if (move.type==ROTATE_LINE_LEFT)
		rotateLine(lab, move.value, -1);
	else if (move.type==ROTATE_COLUMN_UP)
		rotateColumn(lab, move.value, 1);
	else if (move.type==ROTATE_COLUMN_DOWN)
		rotateColumn(lab, move.value, -1);
	else {
		/* pointer to the position of the current player */
		int *pX = lab->player ? &lab->opX : &lab->X;
		int *pY = lab->player ? &lab->opY : &lab->Y;

		if (move.type == MOVE_UP)
			*pY = (*pY - 1) % lab->sizeY;
		else if (move.type == MOVE_DOWN)
			*pY = (*pY + lab->sizeY + 1) % lab->sizeY;    // add sizeY to avoid negative value (modulo of negative value is negative in C...)
		else if (move.type == MOVE_RIGHT)
			*pX = (*pX + 1) % lab->sizeX;
		else if (move.type == MOVE_LEFT)
			*pX = (*pX + lab->sizeX - 1) % lab->sizeX;    // idem
	}
}


void myPrintLaby( t_laby* l)
{
	printf("\nLaby:\n");
	for (int y=0; y < l->sizeY; y++)
	{
        for(int x=0; x<l->sizeX; x++)
        {
			/* treasor */
			if ((x == l->trX) && (y == l->trY))
				printf("!");
			/* opponent */
			else if ((x == l->opX) && (y == l->opY))
				printf("&");
			/* me */
			else if ((x == l->X) && (y == l->Y))
				printf("@");
			else if (l->data[y*l->sizeX+x])
				printf("X");
			else
				printf("-");
		}
		printf("\n");
	}
}


int main()
{

	t_laby laby;						/* data of the labyrinth */
	t_return_code ret = MOVE_OK;		/* indicates the status of the previous move */
	t_move move;						/* a move */

    char toto[100];

	debug=1;	/* enable debug */

	/* connection to the server */
	connectToServer( "localhost", 1234, "THlaby");

	/* play over and over...
	(this loop is not necessary if you only want to play one game, but will be useful for tournament)*/
	while (ret == MOVE_OK)  // while (1)
	{

		/* wait for a game, and retrieve informations about it */
		waitLab( &laby, "PLAY_RANDOM timeout=10 rotate=False");

		do {
			/* display the labyrinth */
			printLabyrinth();
			myPrintLaby(&laby);  /* to compare */

			if (laby.player==1)	/* The opponent plays */
			{
				ret = getMove( &move);
				playMove( &laby, move);
			}
			else
			{
				//.... choose what to play
                move.type = DO_NOTHING;
				ret = sendMove(move);
				playMove( &laby, move);
			}

			/* change player */
			laby.player = ! laby.player;

			scanf("%s",toto);



		} while (ret==MOVE_OK);

		if ( (laby.player==0 && ret==MOVE_WIN) || (laby.player==1 && ret==MOVE_LOSE) )
			printf("\n Unfortunately, the opponent wins\n");
		else
			printf("\n Héhé, I win!!\n");

		/* we do not forget to free the allocated array */
		free(laby.data);
	}

	/* end the connection, because we are polite */
	closeConnection();

	return EXIT_SUCCESS;
}



