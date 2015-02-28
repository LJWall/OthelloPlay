import sys
from os.path import abspath

path = abspath('./..')
if path not in sys.path:
    sys.path.append(path)
    
from othello.othello import OthelloBoardClass, GameCompleteError, InvalidMoveError, NoAvailablePlayError

game = OthelloBoardClass(8)

print(game)