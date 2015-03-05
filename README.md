Basic web app to play Othello (A.K.A. Reversi) against the computer
===================================================================

Developed with Python 3

Requirements:
- Flask 0.10.x.
- mysql.connector Python package
- JS library Sammy 0.7.6 (included in repository)
- Other JS libraries obtained from CDNs

Files
-----

### othello.py

Defines a game class, which keep track of the state of the game 
board, whose turn etc, and allow playing moves, and a basic auto-play 
method.

### test_othello.py

Unit test for above.

### othello_model.py

Handles DB (mySQL) storage.  One class which extends the othello.py 
class, adding properties to stores its own DB keys, and methods to
provide its own URI, and make JSON friendly version of itself.

Key principle if that database stored game states are immutable. I.e.
if a game state is retrieved from the DB, and a move is made, then
upon saving it stores a new version. This is to allow GET-ing of 
earliet game states.

### test_othello_model.py

Unit test for above.

### othello_restpi.py

RESTfull (ish) API using flask, to create new games, play moves, and
get existing game states.

### test_othello_restpi.py

Unit test the above.

### config.cfg

Flask and DB config properties. Amend your own as needed.

### make_table.sql

Table structure for storing the game states. Note, this is for
information only - you will need to set up your own deployment
and/or testing DB environment. Neither this code nor Flask will
create a test environment on the fly. (Unlike Django for example.)

### sammy-0.7.6.min.js

JS framework from http://sammyjs.org

### index.html and othello.js

Single page client for API, using Sammy (included) and other JS
frameworks delivered by CDNs.
