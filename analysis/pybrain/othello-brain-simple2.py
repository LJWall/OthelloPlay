#! /usr/bin/env python3
from othello.othello import OthelloBoardClass
from othello.ml.features import get_game_features
from othello.ml.strategies import strategies

from pybrain.rl.environments.fitnessevaluator import FitnessEvaluator

import matplotlib.pyplot as plt
from numpy import array

from pybrain.tools.shortcuts import buildNetwork
from pybrain.optimization import HillClimber, StochasticHillClimber, RandomSearch

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

class OthelloStrategyEvaluator(FitnessEvaluator):
    results = list()
    plot_machine=None
    def __init__(self, opponents, plot_machine=None):
        self.opponents = opponents
        self.plot_machine = plot_machine
        
    def play_move(self, game, net):
        plays = game.get_plays(simple=False)
        player = game.current_turn
        for p in plays:
            v = get_game_features(plays[p], ['game_progress', 'norm_' + player + '_score', 'safe_' + player, 'corners_' + player])
            plays[p].rank = net.activate(v)[0]
        best_play = max(plays, key=lambda p: plays[p].rank)
        game.play_move(*best_play)
    
    def f(self, net):
        print('.', end='', flush=True)
        ret_value = 0
        for opponent in self.opponents:
            game = OthelloBoardClass(8)
            while not game.game_complete:
                if game.current_turn=='O':
                    self.play_move(game, net)
                else:
                    strategies[opponent](game)
            scores = game.score()
            ret_value += (scores['O'] - scores['X'])/len(self.opponents)
        if self.plot_machine:
            self.plot_machine.push(ret_value)
        return ret_value
    
if __name__ == '__main__':
    store_results = 'nn8-simple2.pickle'
    plt.ion()
    net = buildNetwork(4, 4, 1)
    pm = PlotMachine()
    count = 0
    opponents = ['best_score_strategy_2', 'look_ahead_NN']
    try:
        while True:

            print('\n' + str(count) + '\t', end='')
            count += 1
            task = OthelloStrategyEvaluator(opponents, pm)
            learn_res = StochasticHillClimber(task, net, maxEvaluations=200, desiredEvaluation=30, temperature=1.5).learn()
            opponents.append('random_strategy')
            net = learn_res[0]
            with open(store_results + '.it' + str(count), mode='wb') as F:
                pickle.dump(net, F)
    except KeyboardInterrupt:
        pass
    
    print('Done...')
    
