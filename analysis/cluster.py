#! /usr/bin/env python3
from othello.othello import OthelloBoardClass
from othello.ml.strategies import strategies
import sklearn.cluster as cluster
import pickle

store_results = ''
load_results = 'raw_data6.pickle'
cluster_results = 'cluster_data6.pickle'

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

# Store the results
with open(cluster_results, mode='wb') as F:
    pickle.dump({'cluster_value': prediction_value,
                 'model_object': data_clust,
                 'features': ['norm_X_score', 'game_progress', 'safe_X', 'safe_O'],
                 'sign': {'X': 1, 'O': -1}}, # indicated that for X greater value is better, for O the converse.
                F)  



