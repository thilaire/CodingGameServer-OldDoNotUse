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
	int us;             /* our number player*/
	int player;			/* gives who plays (0: us, 1: the opponent) */
} t_laby;


void waitLab( t_laby* lab, char* training)
{
	char labName[50];					/* name of the labyrinth  - don't care about it*/
	/* wait for labyrinth */
	waitForLabyrinth( training, labName, &(lab->sizeX), &(lab->sizeY));

	/* get the labyrinth */
	lab->data = (char*) malloc( lab->sizeX * lab->sizeY );
	lab->us = getLabyrinth( lab->data);
    lab->player = 0;    /* player 0 always starts */

    /* change the data of the labyrinth (now 0 is empty, -1 is wall) */
    char* data = lab->data;
    for (int i=0; i<lab->sizeX*lab->sizeY; i++,data++)
        *data = -(*data);

	/* initialize the positions */
	lab->trX = lab->sizeX/2;
	lab->trY = lab->sizeY/2;
    lab->opX = lab->us ? 0 : lab->sizeX - 1;
    lab->X = !lab->us ? 0 : lab->sizeX - 1;
	lab->opY = lab->sizeY/2;
	lab->Y = lab->sizeY/2;
}

const int deltaX[4] = {0,0,-1,+1};
const int deltaY[4] = {-1,1,0,0};

void pseudoAstar( t_laby* lab)
{
    char* data = lab->data;
    int d = 1;
    int progress = 1;

    data[ lab->trY * lab->sizeX + lab->trX ] = d;

    while (progress)
    {
        progress = 0;
        for(int x=0; x<lab->sizeX; x++)
        for(int y=0; y<lab->sizeY; y++)
        {
            /* si on est sur une case de distance d, alors on s'occupe de ses voisins */
            if (data[ y * lab->sizeX + x]==d)
            {
                for(int dir=0; dir<4; dir++)
                {
                    int nx = (x+deltaX[dir]+lab->sizeX) % lab->sizeX;
                    int ny = (y+deltaY[dir]+lab->sizeY) % lab->sizeY;
                    /* si c'est un mur, on le tag à la distance d */
                    if (data[ ny*lab->sizeX+nx ]==0)
                    {
                        data[ ny*lab->sizeX+nx ] = d+1;
                        progress = 1;
                    }
                }
            }

        }
        d++;
    }
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
		int *pX = lab->player==lab->us ? &lab->X : &lab->opX;
		int *pY = lab->player==lab->us ? &lab->Y : &lab->opY;

		if (move.type == MOVE_UP)
			*pY = (*pY + lab->sizeY - 1) % lab->sizeY;
		else if (move.type == MOVE_DOWN)
			*pY = (*pY  + 1) % lab->sizeY;    // add sizeY to avoid negative value (modulo of negative value is negative in C...)
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
			else if (l->data[y*l->sizeX+x]==-1)
				printf("X");
			else if (l->data[y*l->sizeX+x]==0)
				printf(".");
			else if (l->data[y*l->sizeX+x]>9)
			    printf("+");
			else
			    printf("%d",l->data[y*l->sizeX+x]);
		}
		printf("\n");
	}
}

/* trouve le meilleur coup, juste en suivant le coup qui nous rapproche du trésor */
t_move bestMove( t_laby* lab)
{
    t_move m;
    /* on regarde les 4 voisins */
    for(int dir=0; dir<4; dir++)
    {
        /* position du voisin */
        int nx = (lab->X+deltaX[dir]+lab->sizeX) % lab->sizeX;
        int ny = (lab->Y+deltaY[dir]+lab->sizeY) % lab->sizeY;

        if (lab->data[ny*lab->sizeX+nx]>0 && lab->data[ny*lab->sizeX+nx] < lab->data[ lab->Y*lab->sizeX+lab->X])
        {
            m.type = MOVE_UP+dir;
            return m;
        }
    }
    printf("On est coincé!\n");
    m.type = DO_NOTHING;
    return m;
}



int main()
{

	t_laby laby;						/* data of the labyrinth */
	t_return_code ret = MOVE_OK;		/* indicates the status of the previous move */
	t_move move;						/* a move */

//char toto[100];

	//debug=1;	/* enable debug */

	/* connection to the server */
	connectToServer( "localhost", 1234, "THlaby");

	/* play over and over...
	(this loop is not necessary if you only want to play one game, but will be useful for tournament)*/
	while (ret == MOVE_OK)  // while (1)
	{

		/* wait for a game, and retrieve informations about it */
		waitLab( &laby, "PLAY_RANDOM timeout=10 rotate=True");

		do {
			/* display the labyrinth */
			printLabyrinth();

            pseudoAstar(&laby);
  			//myPrintLaby(&laby);  /* to compare */

            //scanf("%s",toto);

			if (laby.player!=laby.us)	/* The opponent plays */
			{
				ret = getMove( &move);
				playMove( &laby, move);
			}
			else
			{
				//.... choose what to play
                move = bestMove(&laby);
				ret = sendMove(move);
				playMove( &laby, move);
			}

			/* change player */
			laby.player = ! laby.player;



		} while (ret==MOVE_OK);

		if ( (laby.player==laby.us && ret==MOVE_WIN) || (laby.player!=laby.us && ret==MOVE_LOSE) )
			printf("\n Unfortunately, we loose... :-(\n");
		else
			printf("\n Héhé, I win!!\n");

		/* we do not forget to free the allocated array */
		free(laby.data);
	}

	/* end the connection, because we are polite */
	closeConnection();

	return EXIT_SUCCESS;
}



