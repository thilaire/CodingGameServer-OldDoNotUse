
#include <stdio.h>
#include <stdlib.h>
#include "../clientAPI/labyrinthAPI.h"
#include <unistd.h>


extern int debug;	/* hack to enable debug messages */

typedef struct {
	int sizeX,sizeY;	/* labyrinth size */
	char* data;			/* labyrinth data */
	int trX,trY;		/* treasure position */
	int X,Y;			/* our position */
	int opX,opY;		/* opponent position */
	int player;			/* gives who plays (0: us, 1: the opponent) */
	char name[100];		/* labyrinthe name */
} t_laby;



/* rotate a line of the labyrinth */
void rotateLine( t_laby* laby, int line, int delta)
{
}

/* rotate a column of the labyrinth */
void rotateColumn( t_laby* laby, int column, int delta)
{
}



/* Play a move (change the labyrinth and coordinate accordingly */
void playMove( t_laby* laby, int type, int val)
{
	if (type==ROTATE_LINE_RIGHT)
		rotateLine(laby, val, 1);
	else if (type==ROTATE_LINE_LEFT)
		rotateLine(laby, val, -1);
	else if (type==ROTATE_COLUMN_UP)
		rotateColumn(laby, val, 1);
	else if (type==ROTATE_COLUMN_DOWN)
		rotateColumn(laby, val, -1);
	else {
		/* pointer to the position of the current player */
		int *pX = laby->player ? &laby->X : &laby->opX;
		int *pY = laby->player ? &laby->Y : &laby->opY;

		if (type == MOVE_UP)
			*pY = (*pY + 1) % laby->sizeY;
		else if (type == MOVE_DOWN)
			*pY = (*pY + laby->sizeY - 1) %
				  laby->sizeY;    // add sizeY to avoid negative value (modulo of negative value is negative in C...)
		else if (type == MOVE_RIGHT)
			*pX = (*pX + 1) % laby->sizeX;
		else if (type == MOVE_LEFT)
			*pX = (*pX + laby->sizeX - 1) % laby->sizeX;    // idem
	}
}


void myPrintLaby( t_laby* l)
{
	printf("\nLaby:\n");
	for( int i=0; i<l->sizeX; i++) {
		for (int j = 0; j < l->sizeY; j++) {
			/* treasor */
			if ((i == l->trX) && (j == l->trY))
				printf("X");
			/* opponent */
			else if ((i == l->opX) && (j == l->opY))
				printf("O");
			/* me */
			else if ((i == l->X) && (j == l->Y))
				printf("M");
			else if (l->data[j*l->sizeX+i])
				printf("\u2589");
			else
				printf(" ");
		}
		printf("\n");
	}
}


int main()
{
	char labName[50];	/* name of the labyrinth */
	t_laby lab;
	int finished;		/* indicates if the game is over */
	int type, val;		/* used for a move */

	int x;

	debug=1;	/* enable debug */

	/* connection to the server */
	char nom[50];
	sprintf(nom,"ProgTest_%d",getpid());
	connectToServer( "localhost", 1235, nom);
	printf("Youhou, connecté au serveur !\n");


	/* play over and over... 
	(this loop is not necessary if you only want to play one game, but will be useful for tournament)*/
	while (1)
	{

		/* wait for a game, and retrieve informations about it */
		waitForLabyrinth( lab.name, &(lab.sizeX), &(lab.sizeY));
		lab.data = (char*) malloc( lab.sizeX * lab.sizeY );
		lab.player = getLabyrinth( lab.data);

		lab.trX = lab.sizeX/2;
		lab.trY = lab.sizeY/2;
		if (lab.player) {
			lab.opX = 1;
			lab.X = lab.sizeX - 2;
		}
		lab.opY = lab.sizeY/2;
		lab.X = lab.sizeY/2;

		//printf("Voici le labyrinthe\n");
		//myPrintLaby( &lab);

		printLabyrinth();
			

		do {
			finished=0;
			if (lab.player==1)	/* The opponent plays */
			{
				finished = getMove( &type, &val);
				//playMove( &lab, type, val);
			}
			else
			{
				//.... choose what to play
				type=MOVE_UP;
				val=0;
				finished = sendMove(type, val);
				//playMove( &lab, type, val);
			}
			/* display the labyrinth */
			printLabyrinth();
			/* change player */
			lab.player = !lab.player;

/*
 */
x=rand()*7/RAND_MAX + 1;
sleep(x);
/*
 */

		} while (!finished);
	

		/* we do not forget to free the allocated array */
		free(lab.data);
	}
	
	/* end the connection, because we are polite */
	closeConnection();

	return EXIT_SUCCESS;
}

