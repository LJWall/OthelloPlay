#! /usr/bin/env python3
from othello import OthelloBoardClass, InvalidMoveError, auto_play_move, get_plays
from copy import deepcopy
import unittest
        

class TestOthelloBoardClass(unittest.TestCase):
    def test_board_creation(self):
        game = OthelloBoardClass(6)
        self.assertEqual(str(game), '- - - - - - \n' +
                                    '- - - - - - \n' +
                                    '- - O X - - \n' +
                                    '- - X O - - \n' +
                                    '- - - - - - \n' +
                                    '- - - - - - \n')
    def test_whose_go(self):
        game = OthelloBoardClass(6)
        self.assertEqual(game.current_turn, 'X')
        game.play_move(2, 1)
        self.assertEqual(game.current_turn, 'O')
        
    def test_play_off_board_raisesKeyError(self):
        game = OthelloBoardClass(6)
        with self.assertRaises(KeyError):
            game.play_move(0, -1)
        with self.assertRaises(KeyError):
            game.play_move(6, 1)
            
    def test_play_over_exiting_pieces_raises_error(self):
        game = OthelloBoardClass(6)
        with self.assertRaises(InvalidMoveError):
            game.play_move(2,2)
    
    def test_play_turns_pieces(self):
        game = OthelloBoardClass(6)
        game.play_move(2, 1)
        self.assertEqual(game[(2, 2)], 'X')
    
    
    def test_play_with_no_turn_raises_error(self):
        game = OthelloBoardClass(6)
        with self.assertRaises(InvalidMoveError):
            game.play_move(3, 1)
            
    def test_get_boundary(self):
        game = OthelloBoardClass(6)
        game.play_move(2, 1)
        self.assertEqual(game.get_boundary(), {(1, 0), (1, 1),(1, 2),(1, 3), (1, 4),
                                            (2, 0),(2, 4),
                                            (3, 0), (3, 1),(3, 4),
                                            (4, 1),(4, 2),(4, 3),(4, 4),})
        game.clear()
        game[(5,5)]='X'
        self.assertEqual(game.get_boundary(), {(4, 5),(5, 4),(4, 4)})
    
    def test_diagonal_play(self):
        game = OthelloBoardClass(6)
        game.clear()
        game[(0, 0)]='X'
        game[(0, 1)]='X'
        game[(0, 2)]='X'
        game[(1, 0)]='O'
        game[(1, 1)]='O'
        game.play_move(2, 0)
        self.assertEqual(game[(1, 0)], 'X')
        self.assertEqual(game[(1, 1)], 'X')
        
        
    
    
    def test_bug(self):
        game = OthelloBoardClass(6)
        game.clear()
        game.update({(1,2): 'X',
                    (1,3): 'X',
                    (1,4): 'X',
                    (2,2): 'X',
                    (2,3): 'O',
                    (3,1): 'O',
                    (3,2): 'O',
                    (3,3): 'O',
        })
        with self.assertRaises(InvalidMoveError):
            game.play_move(1, 5)
            
    def test_score(self):
        game = OthelloBoardClass(6)
        game.clear()
        game.update({(1,2): 'X',
                    (1,3): 'X',
                    (1,4): 'X',
                    (2,2): 'X',
                    (2,3): 'O',
        })
        self.assertEqual(game.score(), {'X': 4, 'O': 1})
        
        
            
class TestAutoPlay(unittest.TestCase):
    def test_get_plays(self):
        game = OthelloBoardClass(6)
        plays = get_plays(game)
        self.assertEqual(set(plays.keys()), {(1,2), (2,1), (3, 4), (4, 3)})
        for p in plays:
            game2 = deepcopy(game)
            game2.play_move(*p)
            self.assertEqual(game2, plays[p])
        
    
    def test_auto_play(self):
        game = OthelloBoardClass(6)
        auto_play_move(game)
        self.assertEqual(game.current_turn, 'O')
        self.assertEqual(len(game), 5)
        auto_play_move(game)
        self.assertEqual(game.current_turn, 'X')
        self.assertEqual(len(game), 6)
        
if __name__ == '__main__':
    unittest.main()