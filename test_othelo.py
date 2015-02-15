#! /usr/bin/env python3
from othelo import OtheloBoardClass, InvalidMoveError
import unittest
        

class TestOtheloBoardClass(unittest.TestCase):
    def test_board_creation(self):
        game = OtheloBoardClass(6)
        self.assertEqual(str(game), '- - - - - - \n' +
                                    '- - - - - - \n' +
                                    '- - O X - - \n' +
                                    '- - X O - - \n' +
                                    '- - - - - - \n' +
                                    '- - - - - - \n')
    def test_whose_go(self):
        game = OtheloBoardClass(6)
        self.assertEqual(game.current_turn, 'X')
        game.play_move(2, 1)
        self.assertEqual(game.current_turn, 'O')
        
    def test_play_off_board_raisesKeyError(self):
        game = OtheloBoardClass(6)
        with self.assertRaises(KeyError):
            game.play_move(0, -1)
        with self.assertRaises(KeyError):
            game.play_move(6, 1)
            
    def test_play_over_exiting_pieces_raises_error(self):
        game = OtheloBoardClass(6)
        with self.assertRaises(InvalidMoveError):
            game.play_move(2,2)
    
    def test_play_turns_pieces(self):
        game = OtheloBoardClass(6)
        game.play_move(2, 1)
        self.assertEqual(game[(2, 2)], 'X')
    
    
    def test_play_with_no_turn_raises_error(self):
        game = OtheloBoardClass(6)
        with self.assertRaises(InvalidMoveError):
            game.play_move(3, 1)
        
if __name__ == '__main__':
    unittest.main()