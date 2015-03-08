from othello.othello import OthelloBoardClass, GameCompleteError, NoAvailablePlayError
from othello.ml.strategies import random_strategy, best_score_strategy

from pybrain.rl.environments.fitnessevaluator import FitnessEvaluator

import matplotlib.pyplot as plt
from numpy import array

#from pybrain.tools.shortcuts import buildNetwork
#from pybrain.optimization import HillClimber, StochasticHillClimber

import pickle

def draw_game(game):
    rows = list()
    for x in range(game.size):
        rows.append(list())
        for y in range(game.size):
            state = game.get((x, y), '-')
            if state == 'O':
                rows[x].append(1)
            elif state == 'X':
                rows[x].append(-1)
            else:
                rows[x].append(0)
    plt.pcolor(array(rows))
    plt.pause(0.5)


class OthelloStrategyEvaluator(FitnessEvaluator):
    show = False
    N=5
    def f(self, net):
        print('.', end='', flush=True)
        ret_value = 0
        for _ in range(self.N):
            game = OthelloBoardClass(6)
            while not game.game_complete:
                if self.show:
                    draw_game(game)
                if game.current_turn=='O':
                    plays = game.get_plays(simple=False)
                    for p in plays:
                        v = list()
                        for x in range(game.size):
                            for y in range(game.size):
                                state = plays[p].get((x, y), '-')
                                if state == 'O':
                                    v.append(1)
                                elif state == 'X':
                                    v.append(-1)
                                else:
                                    v.append(0)
                        plays[p].rank = net.activate(v)[0]
                    
                    best_play = max(plays, key=lambda p: plays[p].rank)
                    game.play_move(*best_play)
                else:
                    random_strategy(game)
            scores = game.score()
            ret_value += (scores['O'] - scores['X'])/self.N
            if self.show:
                draw_game(game)
                print((scores['O'] - scores['X']))
            
        return ret_value
    
if __name__ == '__main__':
    plt.ion()

    task = OthelloStrategyEvaluator()
    store_results = 'nn6.pickle.it2'
    
    with open(store_results, mode='rb') as F:
        net = pickle.load(F)  
    
    task.show = True
    task(net)
    
