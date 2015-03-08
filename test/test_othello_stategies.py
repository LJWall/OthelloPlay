#! /usr/bin/env python3
from othello.othello import OthelloBoardClass
from othello.ml.strategies import strategies
import unittest
        

class TestOthelloStrategies(unittest.TestCase):
    """
    Tests that that strategies implement can successfully play a
    game (without raising errors).  Does not test the nature of
    each strategy.
    """
    
    def test_can_play_a_game(self):
        """Play a game to completeion for each strategy. No actual
        assertions, but should not raise any errors."""
        for alg in strategies:
            game = OthelloBoardClass(6)
            while not game.game_complete:
                strategies[alg](game)
    
    def test_can_play_usual_sizes(self):
        """Play two moves on a board of size 8x8 and 10x10. No
        assertions, but should not raise any errors."""
        for alg in strategies:
            game = OthelloBoardClass(8)
            strategies[alg](game)
            strategies[alg](game)
            game = OthelloBoardClass(10)
            strategies[alg](game)
            strategies[alg](game)
        
if __name__ == '__main__':
    unittest.main()