    
from othello.othello import OthelloBoardClass, GameCompleteError, NoAvailablePlayError
from othello.ml.strategies import random_strategy

from pybrain.rl.environments.fitnessevaluator import FitnessEvaluator

import matplotlib.pyplot as plt
from numpy import array

from pybrain.tools.shortcuts import buildNetwork
from pybrain.optimization import HillClimber, StochasticHillClimber
from pybrain.structure import TanhLayer

import pickle

class PlotMachine():
    def __init__(self):
        plt.ion()
        self.data = list()
    
    def push(self, item):
        if item is list:
            self.data += item
        else:
            self.data.append(item)
        plt.plot(self.data)
        plt.pause(0.1)
 
class BestScoreNet():
    def activate(self, board_list):
        return [sum(board_list)]

class OthelloStrategyEvaluator(FitnessEvaluator):
    opponent_nets = None
    results = list()
    plot_machine=None
    def __init__(self, opponent_nets, plot_machine=None):
        self.opponent_nets = opponent_nets
        self.plot_machine = plot_machine
        
    def play_move(self, game, net, sign):
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
            plays[p].rank = sign*net.activate(v)[0]
        best_play = max(plays, key=lambda p: plays[p].rank)
        game.play_move(*best_play)
    
    def f(self, net):
        print('.', end='', flush=True)
        ret_value = 0
        for opponent_net in self.opponent_nets:
            game = OthelloBoardClass(6)
            while not game.game_complete:
                if game.current_turn=='O':
                    self.play_move(game, net, 1)
                else:
                    self.play_move(game, opponent_net, -1)
            scores = game.score()
            ret_value += (scores['O'] - scores['X'])/len(self.opponent_nets)
        if self.plot_machine:
            self.plot_machine.push(ret_value)
        return ret_value
    
if __name__ == '__main__':
    store_results = 'nn6.pickle'
    plt.ion()
    nets = [BestScoreNet(), buildNetwork(36, 20, 1, hiddenclass=TanhLayer),
            buildNetwork(36, 20, 1, hiddenclass=TanhLayer),
            buildNetwork(36, 20, 1, hiddenclass=TanhLayer),
            buildNetwork(36, 20, 1, hiddenclass=TanhLayer)]
    pm = PlotMachine()
    count = 0
    try:
        while True:

            print('\n' + str(count) + '\t', end='')
            count += 1
            task = OthelloStrategyEvaluator(nets[0:4] + nets[-1:], pm)
            learn_res = StochasticHillClimber(task, nets[-1], maxEvaluations=1000, desiredEvaluation=22).learn()
            nets.append(learn_res[0])
            with open(store_results + '.it' + str(count), mode='wb') as F:
                pickle.dump(nets[-1], F)
            if learn_res[1]<22:
                print('Got to: ' + str(learn_res[1]))
                break
    except KeyboardInterrupt:
        pass
    
    print('Done...')
    
