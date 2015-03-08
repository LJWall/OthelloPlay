import random
import pickle
from othello.othello import OthelloBoardClass, GameCompleteError, InvalidMoveError, NoAvailablePlayError
from othello.ml.features import get_game_features
import os

thisdir = os.path.dirname(os.path.realpath(__file__))


# Used to provide a dictionary of strategy functions
class FunctionDict(dict):
    def register(self, name):
        if name in self:
            raise UserWarning # warn on replacment
        def assign_func_name(func):
            func.order = len(self)
            self[name] = func
            return func
        return assign_func_name
    def get_jsonable_object(self):
        ret_dict = {func_name: {'order': self[func_name].order,
                                'desc': self[func_name].__doc__} for func_name in self}
        return ret_dict
strategies = FunctionDict()

def generic_strategy_simple(game, rank):
    """Takes a game an plays move which gives the best score according to passed in
    rank function (which should accept a game object).  Assumes bigger number = better"""
    if game.game_complete:
        raise GameCompleteError
    play_results = game.get_plays(simple=False)
    if len(play_results):
        best = max(rank(play_results[x]) for x in play_results)
        plays = [play for play in play_results if rank(play_results[play])==best]
        i = random.randint(0, len(plays)-1)
        game.play_move(*plays[i])
    else:
        raise NoAvailablePlayError

@strategies.register('Neural net')
def basic_NN(game):
    """Simple neural net used for ranking a board based on four key features."""
    if not getattr(basic_NN, 'net', None):
        with open(thisdir + '/nn6-simple2.pickle.it3', mode='rb') as F:
            basic_NN.net = pickle.load(F)
    net = basic_NN.net
    def rank(g):
        player = g.current_turn
        features = get_game_features(g, ['game_progress', 'norm_' + player + '_score', 'safe_' + player, 'corners_' + player])
        return net.activate(features)[0]
    generic_strategy_simple(game, rank)
    
@strategies.register('Random')
def random_strategy(game):
    """Plays a move at random."""
    generic_strategy_simple(game, lambda x: 1)

@strategies.register('Best score')    
def best_score_strategy(game):
    """Plays the move that gives the best immediate score."""
    generic_strategy_simple(game, lambda x: x.score()[game.current_turn])

@strategies.register('Basic cluster')
def immediate_cluster(game):
    """Play the move that gives the best rank according to game state cluster data."""
    if not getattr(immediate_cluster, 'data', None):
        with open(thisdir + '/cluster_data6.pickle', mode='rb') as F:
            immediate_cluster.data = pickle.load(F)
    cluster = immediate_cluster.data
    def rank(g):
        feature_vect = get_game_features(g, cluster['features'])
        cluster_index = cluster['model_object'].predict([feature_vect])
        return cluster['sign'][game.current_turn]*cluster['cluster_value'][cluster_index]
    generic_strategy_simple(game, rank)

def generic_strategy_look_ahead(game, rank):
    """Plays the move that maximises the rank, assuming the opponents following
    move minimises the rank."""
    if game.game_complete:
        raise GameCompleteError
    play_results = game.get_plays(simple=False)
    if len(play_results):
        for play in play_results:
            if play_results[play].game_complete or (play_results[play].current_turn == game.current_turn):
                play_results[play].rank = rank(play_results[play])
            else:
                follow_ups = play_results[play].get_plays(simple=False)
                play_results[play].rank = min(rank(follow_ups[play2]) for play2 in follow_ups)
        best = max(play_results[play].rank for play in play_results)    
        plays = [play for play in play_results if play_results[play].rank==best]
        i = random.randint(0, len(plays)-1)
        game.play_move(*plays[i])
    else:
        raise NoAvailablePlayError

@strategies.register('Neural net (2)')
def look_ahead_NN(game):
    """Simple neural net used for ranking a board based on four key features; looks ahead as far as opponent's response."""
    if not getattr(look_ahead_NN, 'net', None):
        with open(thisdir + '/nn6-simple2.pickle.it3', mode='rb') as F:
            look_ahead_NN.net = pickle.load(F)
    net = look_ahead_NN.net
    def rank(g):
        player = g.current_turn
        features = get_game_features(g, ['game_progress', 'norm_' + player + '_score', 'safe_' + player, 'corners_' + player])
        player_opp = 'X' if player=='O' else 'O'
        features_opp = get_game_features(g, ['game_progress', 'norm_' + player_opp + '_score', 'safe_' + player_opp, 'corners_' + player_opp])
        return net.activate(features)[0] - net.activate(features_opp)[0]
    generic_strategy_look_ahead(game, rank)  

@strategies.register('Best score (2)')    
def best_score_strategy_2(game):
    """Plays the move that minimises the opponent's maximum score following one additional play."""
    generic_strategy_look_ahead(game, lambda x: x.score()[game.current_turn])

@strategies.register('Basic cluster (2)')    
def cluster_strategy_2(game):
    """Plays the move that minimises the opponents best ranking (based on cluster data) following one additional play."""
    if not getattr(cluster_strategy_2, 'data', None):
        with open(thisdir + '/cluster_data6.pickle', mode='rb') as F:
            cluster_strategy_2.data = pickle.load(F)
    cluster = cluster_strategy_2.data
    def rank(g):
        feature_vect = get_game_features(g, cluster['features'])
        cluster_index = cluster['model_object'].predict([feature_vect])
        return cluster['sign'][game.current_turn]*cluster['cluster_value'][cluster_index]
    generic_strategy_look_ahead(game, rank)

if __name__ == '__main__':
    print(strategies)