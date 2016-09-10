#ifndef __API_CLIENT_LABYRINTH__
#define __API_CLIENT_LABYRINTH__

/*

...

*/




/*
Initialize connection with the server
Parameters:
- serverName: (string) address of the server (it could be "localhost" if the server is run in local, or "pc4521.polytech.upmc.fr" if the server runs there)
 - name: (string) name of the bot

Quit the program if the connection to the server cannot be established
*/
void connectToServer( char* serverName, char* name);


/* close the connection 
USEFUL?
*/
void closeConnection();



/* wait for a labyrinth, and retrieve its name and size
Parameters:
- labyrinthName: char* (max 50 characters), corresponds to the labyrinth name
- sizeX and sizeY: int*, size of the labyrinth */
void waitForLabyrinth( char* labyrinthName, int* sizeX, int* sizeY);




#define END_OF_DATA	0
#define WALL		1
#define US			2
#define OPPONENT	3
#define TREASURE	4



/* fill the char* data with the data of the labyrinth
 * 	0 if there is no more data to retrieve
	1 for a wall
	2 for your position
	3 for the opponent
	4 for the treasure

the pointer data MUST HAVE allocated with the right size !! */
void getLabyrinth( char* data);



/* returns 0 if it's your turn, or 1 if it's the opponent's turn 
Useful in the beginning, to know who starts
*/
int getWhoStarts();


/* get the move of the opponent / send our move
A move is a tuple (type,value):
- type can be ROTATE_LINE_UP, ROTATE_LINE_DOWN, ROTATE_COLUMN_UP, ROTATE_COLUMN_DOWN, MOVE_LEFT, MOVE_RIGHT, MOVE_UP or MOVE_DOWN
- in case of rotation, the value indicates the number of the line (or column) to be rotated
Returns 1 if the game is finished, 0 otherwise */
#define ROTATE_LINE_UP		0
#define ROTATE_LINE_DOWN	1
#define ROTATE_COLUMN_UP	2
#define ROTATE_COLUMN_DOWN	3
#define MOVE_UP				4
#define MOVE_DOWN			5
#define MOVE_LEFT			6
#define MOVE_RIGHT			7
int getMove( int* type, int* val);
int sendMove(int type, int val);

/* display the labyrinth */
void printLabyrinth();

/* send a comment */
void sendComment(char* comment);



#endif