# General connection protocol

This file gives the **intern** details about the connection protocol between the player (client) and the server. 
For the server, the functions concerned are in `server/Player/PlayerSocket.py`, and for the client in `clientAPI/C/clientAPI.c` (we give in parenthesys the name of the functions/methods concerned).

Here are (in that order), the different actions:

1. Client opens TCP connection on server HOST and port PORT         (client:`connectToCGS`, server:`handle`)

2. Name of the client       (client: `connectToServer`, server: `handle` and `getPlayerName`)
   1. Client sends `"CLIENT_NAME %s"` with its name (max 20 char. in `[a-zA-Z0-9_]`)
   2. Server acknowledges (send `"OK"`) if the name is valid

3) Waiting for a game       (client: `waitForGame`, server: `waitForGame`)
   1. Client sends `"WAIT_GAME %s"` with the type of the game (an empty string for a regular game, or the name of the type, like `"DO_NOTHING"`)
   2. Server acknowledges (send `"OK"`)
   3. Server waits for the game to start
   4. Server sends `"%s"` the name of the game
   5. Server sends `"%s"` the data of the game (the size of the labyrinth, for example)

4) Get the full datas of the game       (client: `getGameData`, server: `sendGameData`)
   1. Client sends `"GET_GAME_DATA"`
   2. Server acknowledges (send `"OK"`)
   3. Server sends `"%s"` the datas of the game (an array for example)
   4. Server sends `"%d"` who plays next (`0` => it's the client's turn, `1` => it's the opponent's turn).
   This also indicates if the player is player0 or player1, since player0 always starts

Now the client can send any of the following command (until the end of the game):

5) Get the opponent's move          (client: `getCGSMove`, server: `handle`)
   1. Client sends `"GET_MOVE"`
   2. Server acknowledges (send `"OK"`) if it's the opponent's turn to play
   3. Server waits the opponent's last move (and synchronize the two clients)
   4. Server plays this move
   5. Server sends `"%s"` the move
   6. Server sends `"%d"` the return_code (0 for move ok, +1 for winning move, -1 for losing move)

6) Send its move            (client: `sendCGSMove`, server:`handle`)
   1. Client sends "PLAY_MOVE %s" with its move
   2. Server acknowledge (send `"OK"`) if it's the client's turn to play
   3. Server waits for the `GET_MOVE` of the opponent (and synchronize the two clients)
   4. Server sends `"%d"` the return_code (0 for move ok, +1 for winning move, -1 for losing move)
   5. Server sends associated message `"%s"` (should give more indications about the move, to be printed (e.g "move illegal because..."))

7) Ask string to display the game       (client: `printGame`, server: `handle`)
   1. Client sends `"DISP_GAME"`
   2. Server acknowledge (send `"OK"`)
   3. Server sends `"%s"` a string corresponding to the game
   4. Client displays it

8) Send a comment       (client: `sendCGSComment`, server: `handle`)
   1. Client sends `"SEND_COMMENT %s"`
   2. Server acknowledges (send `"OK"`)
   3. Server publishes this important comment

When the game ends, the client can go to step 3 (it is already connected, the server already knows its name)


Each game defines its own API, that maps to the functions in `clientAPI/C/clientAPI.c`.