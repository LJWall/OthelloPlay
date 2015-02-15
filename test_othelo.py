from othelo import OtheloBoardClass
import unittest # import TestCase, main

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
        game.play_move(0, 2)
        self.assertEqual(game.current_turn, 'O')
        
        
if __name__ == '__main__':
    unittest.main()