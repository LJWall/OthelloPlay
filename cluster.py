#! /usr/bin/env python3
from othello.othello import OthelloBoardClass, GameCompleteError, InvalidMoveError, NoAvailablePlayError
from othello.ml.strategies import strategies
from othello.ml.features import features, get_game_features
import matplotlib.pyplot as plt
import pickle

store_results = 'data.pickle'
load_results = ''


def generate_data(N_games, game_size, features, record_points):
    player = {'X': 'random',
              'O': 'random'}
    results = list()
    for x in range(N_games):
        game = OthelloBoardClass(game_size)
        records = list()
        while not game.game_complete:
            strategies[player[game.current_turn]](game)
            if len(game) in record_points:
                records.append(get_game_features(game, features))
        final_features = get_game_features(game, features)
        for snap_shot in records:
            results.append([snap_shot, final_features])
        print('.', flush=True, end='')
    print('')
    return results
        
        
if len(load_results):
    with open(load_results, mode='rb') as F:
        results = pickle.load(F)
else:
    results = generate_data(1000, 6, ['norm_X_score', 'game_progress', 'safe_X', 'safe_O'], [6*6*3//4])

if len(store_results) and len(load_results)==0:
    with open(store_results, mode='wb') as F:
        pickle.dump(results, F)

x1 = [2*dp[0][0] - dp[0][1] for dp in results] # Black lead at 3/4 point
x2 = [dp[0][2] - dp[0][3] for dp in results] # Black lead in "safe points"
y = [2*dp[1][0] - dp[1][1] for dp in results] # Black lead at end
plt.figure(1)
plt.title('Lead at end vs lead at 3/4')
plt.plot(x1, y, 'ro')
plt.axis([min(x1)-0.05, max(x1)+0.05, min(y)-0.05, max(y)+0.05])
plt.figure(2)
plt.title('Lead at end vs lead in "safe points" at 3/4')
plt.plot(x2, y, 'ro')
plt.axis([min(x2)-0.05, max(x2)+0.05, min(y)-0.05, max(y)+0.05])
plt.show()

