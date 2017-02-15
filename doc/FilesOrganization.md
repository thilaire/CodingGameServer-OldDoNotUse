# Files Organization

The Coding Game Server is organized as follows:

- `runCGS.py`: is the main file, that launchs the server (`python runCGS.py --help` to get its arguments)
- the `clientAPI/` folder contains the different APIs for the client (only
- the `doc/` folder contains the doc
 in C for the moment, but Python API should arrive), that 
- the `games/` folder contains the different games (actually the Labyrinth game in `Labyrinth/`, and a template for new game in `TemplateGame/`)
- and the `server/` folder contains all the CGS server

## The `server/` folder

- `BaseClass.py`: base class for the tournament, players and games
- `Comments.py`: small class for the comments
- `Constants.py`: contains all the constants of the server
- `Game.py`: class for the Games
- `Logger.py`: some fonctions to create loggers for the games, players and tournaments
- `Webserver.py`: contains the routes for the webserver (and its configuration)
- `Player/` contains the class about the players:
  - `Player.py`: the `Player` and `TrainingPlayer` classes
  - `RegularPlayer.py`: main class for the player
  - `PlayerSocket.py`: class that manages all the TCP server and socket connection to the client
- `templates/`: contains all the common web files (HTML, CSS and Javascript) for the web server
- `Tournament/`: all for the tournaments:
  - `Tournament.py`: main class for the tournaments
  - `League.py`, `PoolKnockout.py` and `SingleElimination.py`: the three kind of tournaments (`SingleElimination` is not functionnal, yet)

## a game folder
All the games are in folder  `games/`. Each game should follow the following scheme:
- the dedicated API (that uses the files in `clientAPI/`) are in a `API/` folder
- the doc is in `doc/`
- the logs are by default `logs/` (this may be changed in `runCGS.py` or using the `--logs=<folder>` parameter when running CGS)
- the `server/` folder contains the classes for the game:
  - It may contains a file `xxx.py` (where xxx is the name of the game), with a class `xxx` inside (that inherits from the `Game` class).
  - It may have a `templates/` folder that contains the web files (HTML, CSS and Javascript) dedicated to the game (the webserver will first look in that folder, and then in `server/templates/` for any requested webfile).
- and the various programs (clients) for this game should be in `src/` (but this is not mandatory)

You can have a look at the `Labyrinth` game for details.