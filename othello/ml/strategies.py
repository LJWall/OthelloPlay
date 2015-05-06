import random
import pickle
from othello.othello import OthelloBoardClass, GameCompleteError, InvalidMoveError, NoAvailablePlayError
from othello.ml.features import get_game_features
import os

thisdir = os.path.dirname(os.path.realpath(__file__))

with open(thisdir + '/nn6-simple2.pickle.it3', mode='rb') as F:
    NN_6 = pickle.load(F)
with open(thisdir + '/nn8-simple2.pickle.it4', mode='rb') as F:
    NN_8 = pickle.load(F)




# Used to provide a dictionary of strategy functions
class FunctionDict(dict):
    def register(self, name, good=True):
        def assign_func_name(func):
            func.order = len(self)
            func.good = good
            func.nice_name = name
            self[func.__name__] = func
            return func
        return assign_func_name
    def get_jsonable_object(self, use_all=False):
        ret_dict = {func_name: {'order': self[func_name].order,
                                'nice_name':  self[func_name].nice_name,
                                'desc': self[func_name].__doc__} for func_name in self if use_all or self[func_name].good}
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

@strategies.register('Neural net', False)
def basic_NN(game):
    """Simple neural net used for ranking a board based on four key features."""
    #if not getattr(basic_NN, 'net', None):
    #    with open(thisdir + '/nn6-simple2.pickle.it3', mode='rb') as F:
    #        basic_NN.net = pickle.load(F)
    net = NN_6
    def rank(g):
        player = g.current_turn
        features = get_game_features(g, ['game_progress', 'norm_' + player + '_score', 'safe_' + player, 'corners_' + player])
        return net.activate(features)[0]
    generic_strategy_simple(game, rank)
    
@strategies.register('Random')
def random_strategy(game):
    """Plays a move at random."""
    generic_strategy_simple(game, lambda x: 1)

@strategies.register('Best score', False)
def best_score_strategy(game):
    """Plays the move that gives the best immediate score."""
    generic_strategy_simple(game, lambda x: x.score()[game.current_turn])

@strategies.register('Cluster', False)
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

@strategies.register('Neural net')
def look_ahead_NN(game):
    """Simple neural net for ranking based on four key features. Looks two moves ahead."""
    #if not getattr(look_ahead_NN, 'net', None):
    #    with open(thisdir + '/nn6-simple2.pickle.it3', mode='rb') as F:
    #        look_ahead_NN.net = pickle.load(F)
    if game.size == 6:
        net = NN_6
    else:
        net = NN_8
    def rank(g):
        player = game.current_turn
        player_opp = 'X' if player=='O' else 'O'
        features = get_game_features(g, ['game_progress', 'norm_' + player + '_score', 'safe_' + player, 'corners_' + player])
        features_opp = get_game_features(g, ['game_progress', 'norm_' + player_opp + '_score', 'safe_' + player_opp, 'corners_' + player_opp])
        return net.activate(features)[0] - net.activate(features_opp)[0]
    generic_strategy_look_ahead(game, rank)  

@strategies.register('Best score')    
def best_score_strategy_2(game):
    """Based solely on score.  Looks two moves ahead."""
    generic_strategy_look_ahead(game, lambda x: x.score()[game.current_turn])

@strategies.register('Cluster', False)
def cluster_strategy_2(game):
    """Based on cluster analysis on four key features.  Looks two moves ahead."""
    if not getattr(cluster_strategy_2, 'data', None):
        with open(thisdir + '/cluster_data6.pickle', mode='rb') as F:
            cluster_strategy_2.data = pickle.load(F)
    cluster = cluster_strategy_2.data
    def rank(g):
        feature_vect = get_game_features(g, cluster['features'])
        cluster_index = cluster['model_object'].predict([feature_vect])
        return cluster['sign'][game.current_turn]*cluster['cluster_value'][cluster_index]
    generic_strategy_look_ahead(game, rank)

def depth_search_generic_stratgy(game, rank, depth):
    def alpha_beta(game, rank, depth, alpha, beta, maximise=True, first=False):
        """Depth search using alpha-beta pruning, with given rank function to given depth."""
        if game.game_complete or depth<=0:
            return rank(game), None
        player = game.current_turn
        if maximise:
            ret = -1e10
            for play, result in game.iter_plays(simple=False):
                if not result.current_turn == player:
                    follow_up_rank = alpha_beta(result, rank, depth-1, alpha, beta, not maximise)[0]
                else:
                    follow_up_rank = alpha_beta(result, rank, depth-2, alpha, beta, maximise)[0]
                if follow_up_rank > ret:
                    ret = follow_up_rank
                    best_play = play
                alpha = max(alpha, ret)
                if alpha >= beta:
                    break
            if first:
                game.play_move(*best_play)
            return ret, best_play
        else:
            ret = 1e10
            for play, result in game.iter_plays(simple=False):
                if not result.current_turn == player:
                    follow_up_rank = alpha_beta(result, rank, depth-1, alpha, beta, not maximise)[0]
                else:
                    follow_up_rank = alpha_beta(result, rank, depth-2, alpha, beta, maximise)[0]
                if follow_up_rank < ret:
                    ret = follow_up_rank
                    best_play = play
                beta = min(beta, ret)
                if alpha >= beta:
                    break
            if first:
                game.play_move(*best_play)
            return ret, best_play
    alpha_beta(game, rank, depth, -1e10, 1e10, True, True)


@strategies.register('Neural net (depth search)')
def depth_NN(game):
    """
    Simple neural net for ranking based on four key features. Looks 4 moves ahead using
    basic alpha-beta pruning.  Strong on 6x6.  Slow (and not that strong) on bigger boards.
    """
    #if not getattr(look_ahead_NN, 'net', None):
    #    with open(thisdir + '/nn6-simple2.pickle.it3', mode='rb') as F:
    #        look_ahead_NN.net = pickle.load(F)
    #net = look_ahead_NN.net
    if game.size == 6:
        net = NN_6
    else:
        net = NN_8
    def rank(g):
        player = game.current_turn
        player_opp = 'X' if player=='O' else 'O'
        features = get_game_features(g, ['game_progress', 'norm_' + player + '_score', 'safe_' + player, 'corners_' + player])
        features_opp = get_game_features(g, ['game_progress', 'norm_' + player_opp + '_score', 'safe_' + player_opp, 'corners_' + player_opp])
        return net.activate(features)[0] - net.activate(features_opp)[0]
    depth_search_generic_stratgy(game, rank, 4)  

if __name__ == '__main__':
    print(strategies)