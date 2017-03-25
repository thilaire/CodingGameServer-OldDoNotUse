# CodingGameServer
CodingGameServer (CGS) is a framework to create some Coding Games.

## What do you call **Coding Game** ?
To involve our (undergraduate) students into their programming lecture (mainly `C`), we gave them the opportunity to show their skills in a programming contest based on a game, different every year.
The game considered are mainly turn-based, two players games, like the chess, othelo or checkers (not necesseraly a [zero-sum games](https://en.wikipedia.org/wiki/Zero-sum_game), but it could).
Our students have to write a program, based on a simple API, to play that game agains other students (or against some training players). For that, they need to use what they learn in class, and code some algorithms, like [min-max](https://en.wikipedia.org/wiki/Minimax), [A*](https://en.wikipedia.org/wiki/A*_search_algorithm), etc.

## So, what is CodingGameServer ?
CGS is a (simple) framework to create such a contest.
To play the games, we need:
- a server that the players, and mainly all the game (synchronize the players, create the games, play the games from the players move, define the game rules, etc.)
- an API used to write the player programs (this API provides functions to connect to the server, get back the data from the game, send a move or get the move of the opponent, etc.)
- optionally, a web-server to interact with the server and manage the tournaments, display the games, etc.

So, CGS provides a (complete) framework to set up such a server (and web-server), with dedicated API. For the moment, it is supplied with only one game (Labyrinth), but it has been design in order to ease the writing for a new game (you will have **only** to write code to manage the rules of your game and to display it).



## How to run it ?
Before using it for your own game, the 1st thing is to try it with the Labyrinth game.
You need:
- Python 3.4+
- the following packages: `colorama`, `colorlog`, `docopt`, `bottle`, `jinja2`, `ansi2html`, `karellen-geventws`.
Type `pip install colorama colorlog docopt bottle jinja2 ansi2html karellen-geventws` to install them.

Finally, to run it:
```
./runCGS.py Labyrinth --dev
```
It will run the TCP server on port 1234, and the webserver on port 8088 (you can change those port on command-line, see the help with `./runCGS --help`). Note that the `--dev` option is to run it in `dev` mode (ie do some logging in `games/Labyrinth/logs/` to know what's going on)
Remark: this have only been tested on Unix-based OS (only on Linux and Mac OS), but it *should* work on Windows (...or not...)

You can connect to the webserver (by opening the webpage [http://localhost:8088](http://localhost:8088/) ) and check how ugly our webpages are for the moment (the functionality are present, so in fact we just need to write some fancy templates instead of the ugly ones...).

Then, you can connect your player to make it play....
Wait, you need to write your own player, for that...

Ok, you can use the API provided (see `games/Labyrinth/API/LabyrinthAPI.h`) to connect to the server, wait for a game, and then play an intense game ! It's your turn to code !!
(or you can directly have a look at the different simple programs we wrote as a tutorial for Labyrinth in folder `games/Labyrinth/src/`, as a basis to start)

