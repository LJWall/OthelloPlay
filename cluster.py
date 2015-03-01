#! /usr/bin/env python3
from othello.othello import OthelloBoardClass #, GameCompleteError, InvalidMoveError, NoAvailablePlayError
from othello.ml.strategies import strategies
#from othello.ml.features import features, get_game_features
#import matplotlib.pyplot as plt
import sklearn.cluster as cluster
import pickle

store_results = ''
load_results = 'data6.pickle'


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
    

store_pts = [6, 12, 18, 24, 30]

# load or generate data
if len(load_results):
    with open(load_results, mode='rb') as F:
        results = pickle.load(F)
else:
    results = generate_data(1500, 6, ['norm_X_score', 'game_progress', 'safe_X', 'safe_O'], store_pts)
    if len(store_results):
        with open(store_results, mode='wb') as F:
            pickle.dump(results, F)

print(['norm_X_score', 'game_progress', 'safe_X', 'safe_O'])

# cluster and gentrate average game result for each cluser
data_clust = cluster.KMeans(n_clusters=30, max_iter=1000)
cluster_index = data_clust.fit_predict([dp[0] for dp in results])
prediction_value = list()
for i in range(len(data_clust.cluster_centers_)):
    prediction_value.append(sum([(2*results[j][1][0]-results[j][1][1]) for j in range(len(results)) if cluster_index[j]==i]))
    prediction_value[-1] /= sum([1 for j in cluster_index if j==i])
for i in range(len(data_clust.cluster_centers_)):
    print(str(data_clust.cluster_centers_[i]) + ' :: ' + str(prediction_value[i]))

quit()

# produce plots
#for i in range(5):
#    x1 = [2*dp[0][0] - dp[0][1] for dp in results if round(dp[0][1]*36)==store_pts[i]] # Black lead at 3/4 point
#    x2 = [dp[0][2] - dp[0][3] for dp in results if round(dp[0][1]*36)==store_pts[i]] # Black lead in "safe points"
#    y = [2*dp[1][0] - dp[1][1] for dp in results if round(dp[0][1]*36)==store_pts[i]] # Black lead at end
#    plt.figure(2*i+1)
#    plt.title('Lead at end vs lead at ' + str(store_pts[i]))
#    plt.plot(x1, y, 'ro')
#    plt.axis([min(x1)-0.05, max(x1)+0.05, min(y)-0.05, max(y)+0.05])
#    plt.figure(2*i+2)
#    plt.title('Lead at end vs lead in "safe points" at ' + str(store_pts[i]))
#    plt.plot(x2, y, 'ro')
#    plt.axis([min(x2)-0.05, max(x2)+0.05, min(y)-0.05, max(y)+0.05])
#plt.show()



