import random
import pickle
from othello.othello import OthelloBoardClass, GameCompleteError, InvalidMoveError, NoAvailablePlayError
from othello.ml.features import get_game_features

# Used to provide a dictionary of strategy functions
class FunctionDict(dict):
    def register(self, name):
        def assign_func_name(func):
            self[name] = func
            return func
        return assign_func_name
strategies = FunctionDict()
            
@strategies.register('random')
def random_strategy(game):
    """Plays a move at random."""
    if game.game_complete:
        raise GameCompleteError
    play_results = game.get_plays(simple=True)
    if len(play_results):
        i = random.randint(0, len(play_results)-1)
        play = sorted(play_results.keys())[i]
        game.play_move(*play)
    else:
        raise NoAvailablePlayError

@strategies.register('best_score')    
def best_score_strategy(game):
    """Plays the move that gives the best immediate score."""
    if game.game_complete:
        raise GameCompleteError
    play_results = game.get_plays(simple=True)
    if len(play_results):
        max_flips = max([play_results[x] for x in play_results])
        plays = [key for key in play_results if play_results[key]==max_flips]
        i = random.randint(0, len(plays)-1)
        game.play_move(*plays[i])
    else:
        raise NoAvailablePlayError

@strategies.register('immediate_cluster')
def immediate_cluster(game):
    """Play the move that gives the best rank accordin to the cluster data."""
    if not getattr(immediate_cluster, 'data', None):
        with open('cluster_data6.pickle', mode='rb') as F:
            immediate_cluster.data = pickle.load(F)
    play_results = game.get_plays()
    if len(play_results):
        for p in play_results:
            feature_vect = get_game_features(play_results[p], immediate_cluster.data['features'])
            cluster_index = immediate_cluster.data['model_object'].predict([feature_vect])
            play_results[p].cluster_rank = immediate_cluster.data['cluster_value'][cluster_index]
        if game.current_turn == 'X':
            play = max(play_results, key=(lambda p: play_results[p].cluster_rank))
        else:
            play = min(play_results, key=(lambda p: play_results[p].cluster_rank))
        game.play_move(*play)
    else:
        raise NoAvailablePlayError


if __name__ == '__main__':
    print(strategies)