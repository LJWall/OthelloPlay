import random
import pickle
from othello.othello import OthelloBoardClass, GameCompleteError, InvalidMoveError, NoAvailablePlayError
from othello.ml.features import get_game_features

# Used to provide a dictionary of strategy functions
class FunctionDict(dict):
    def register(self, name, sizes = None):
        if name in self:
            raise UserWarning # warn on replacment
        def assign_func_name(func):
            func.order = len(self)
            func.sizes  = sizes
            self[name] = func
            return func
        return assign_func_name
    def get_jsonable_object(self):
        ret_dict = {func_name: {'order': self[func_name].order,
                                'desc': self[func_name].__doc__} for func_name in self}
        for func_name in self:
            if self[func_name].sizes is not None:
                ret_dict[func_name]['sizes'] = self[func_name].sizes
        return ret_dict
strategies = FunctionDict()
            
@strategies.register('Random')
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

@strategies.register('Best score')    
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

@strategies.register('Basic cluster', [6])
def immediate_cluster(game):
    """Play the move that gives the best rank according to game state cluster data."""
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