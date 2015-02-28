import sys
from os.path import abspath

path = abspath('./..')
if path not in sys.path:
    sys.path.append(path)
    
from othello.othello import OthelloBoardClass, GameCompleteError, InvalidMoveError, NoAvailablePlayError
from strategies import strategies

player = {'X': 'best_score',
          'O': 'best_score'}

win_count = {'X': 0, 'O': 0, 'draw': 0}

for x in range(100):
    game = OthelloBoardClass(6)
    while not game.game_complete:
        strategies[player[game.current_turn]](game)
    score = game.score()
    if score['X'] > score['O']:
        win_count['X'] += 1
        print('X', end='', flush=True)
    elif score['X'] < score['O']:
        win_count['O'] += 1
        print('O', end='', flush=True)
    else:
        win_count['draw'] += 1
        print('.', end='', flush=True)

print('')
    
print('Black ({0}): {1}'.format(player['X'], win_count['X']))
print('White ({0}): {1}'.format(player['O'], win_count['O']))
print('Draws: ' + str(win_count['draw']))



