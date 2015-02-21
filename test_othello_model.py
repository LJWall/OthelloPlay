#! /usr/bin/env python3
import othello_restapi
import othello_model
import othello
import unittest
import mysql.connector
import pickle
from flask import url_for

othello_restapi.app.config.update(
    {'DATABASE_USER': 'unittester',
    'DATABASE_PASSWORD': 'unittester',
    'DATABASE_NAME': 'othello_unittest',
    'DATABASE_HOST': '127.0.0.1',
    'TESTING': True,
    'SERVER_NAME': 'TEST'})



class OthelloBoardModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.board_store = othello_model.BoardStore()
        cls.db_conn = mysql.connector.connect(user='unittester',
                                            password='unittester',
                                            database='othello_unittest',
                                            host='127.0.0.1',
                                            autocommit=True)
        
    @classmethod
    def tearDownClass(cls):
        if getattr(cls, 'db_conn', None):
            cls.db_conn.cmd_query('DELETE FROM othello_data;')  
            cls.db_conn.close()
        
    def setUp(self):
        self.db_conn.cmd_query('DELETE FROM othello_data;')
    
    def test_othelolo_board_model_implments_othello_board_class(self):
        game = othello_model.OthelloBoardModel(6)
        self.assertIsInstance(game, othello.OthelloBoardClass)
        self.assertEqual(game.size, 6)
        
    def test_board_store_saves_board(self):
        game = othello_model.OthelloBoardModel(6)
        self.board_store.save_board(game)
        cur = self.db_conn.cursor()
        cur.execute('SELECT game FROM othello_data;')
        results = cur.fetchall()
        self.assertEqual(len(results), 1)
        storedgame = pickle.loads(results[0][0])
        self.assertEqual(game, storedgame) # note - this is only checking the dictionary part
        self.assertEqual(game.game_key,storedgame.game_key)
        self.assertEqual(game.move_id,storedgame.move_id)
        self.assertEqual(game.last_move_id,storedgame.last_move_id)
        
        
    def test_storing_new_board_populates_ids(self):
        game = othello_model.OthelloBoardModel(6)
        self.board_store.save_board(game)
        self.assertIsNot(game.game_key, None)
        self.assertIsNot(game.move_id, None)
    
    def test_can_store_multiple_boards(self):
        game1 = othello_model.OthelloBoardModel(6)
        game2 = othello_model.OthelloBoardModel(8)
        self.board_store.save_board(game1)
        self.board_store.save_board(game2) # test may fail if this raises error
        
    def test_object_key_match_db_keys(self):
        game = othello_model.OthelloBoardModel(6)
        self.board_store.save_board(game)
        cur = self.db_conn.cursor()
        cur.execute('SELECT game, game_key, move_id FROM othello_data;')
        results = cur.fetchall()
        self.assertEqual(len(results), 1)
        storedgame = pickle.loads(results[0][0])
        self.assertEqual(storedgame.game_key, results[0][1])
        self.assertEqual(storedgame.move_id, results[0][2])
        
    def test_playing_a_manual_move_zaps_move_id(self):
        game = othello_model.OthelloBoardModel(6)
        game.move_id = 0
        game.play_move(2, 1)
        self.assertIs(game.move_id, None)
        self.assertEqual(game.last_move_id, 0)
    
    def test_playing_a_test_move_doesnt_change_move_id(self):
        game = othello_model.OthelloBoardModel(6)
        game.move_id = 0
        result = game.play_move(2, 1, True)
        self.assertEqual(game.move_id, 0)
        self.assertEqual(result, 1)
    
    def test_calling_plays_doesnt_change_move_id(self):
        game = othello_model.OthelloBoardModel(6)
        game.move_id = 0
        result = game.get_plays()
        self.assertEqual(game.move_id, 0)
        
    def test_playing_a_manual_move_doesnt_zap_move_id_on_error(self):
        game = othello_model.OthelloBoardModel(6)
        game.move_id = 0
        try:
            game.play_move(2, 2)
        except BaseException:
            pass
        self.assertEqual(game.move_id, 0)
    
    def test_playing_auto_move_zaps_move_id(self):
        game = othello_model.OthelloBoardModel(6)
        game.move_id = 0
        game.auto_play_move()
        self.assertIs(game.move_id, None)
        self.assertEqual(game.last_move_id, 0)
    
    def test_get_board(self):
        game = othello_model.OthelloBoardModel(6)
        self.board_store.save_board(game)
        game_reread = self.board_store.get_board(game.game_key, game.move_id)
        self.assertEqual(game, game_reread)
        self.assertEqual(game.game_key,game_reread.game_key)
        self.assertEqual(game.move_id,game_reread.move_id)
        self.assertEqual(game.last_move_id,game_reread.last_move_id)
        
    def test_get_board_bad_IDs(self):
        with self.assertRaises(othello_model.GameNotFoundError):
            self.board_store.get_board('99999', 0)
            
    def test_attempt_to_save_board_with_keys_already_set_raies_error(self):
        game = othello_model.OthelloBoardModel(6)
        game.game_key = '100'
        game.move_id = 0
        with self.assertRaises(othello_model.GameAlreadyStoredError):
            self.board_store.save_board(game)
            
    def test_save_following_move(self):
        game = othello_model.OthelloBoardModel(6)
        self.board_store.save_board(game)
        game2 = self.board_store.get_board(game.game_key, game.move_id)
        game2.auto_play_move()
        self.board_store.save_board(game2)
        self.assertEqual(game2.game_key, game.game_key)
        self.assertEqual(game2.move_id, game.move_id+1)
        self.assertEqual(game2.last_move_id, game.move_id)
        
    def test_saving_branching_games(self):
        game = othello_model.OthelloBoardModel(6)
        self.board_store.save_board(game)
        game2 = self.board_store.get_board(game.game_key, game.move_id)
        game2.auto_play_move()
        self.board_store.save_board(game2)
        game3 = self.board_store.get_board(game.game_key, game.move_id)
        game3.play_move(3, 4)
        self.board_store.save_board(game3)
        self.assertEqual(game3.game_key, game.game_key)
        self.assertEqual(game3.move_id, game.move_id+2)
        self.assertEqual(game3.last_move_id, game.move_id)
        
    def test_get_board_URIs(self):
        game = othello_model.OthelloBoardModel(6)
        self.board_store.save_board(game)
        with othello_restapi.app.app_context():
            self.assertEqual(game.get_uri(), url_for('get_game', game_id=game.game_key, move_id=game.move_id))
            self.assertEqual(game.post_uri(), url_for('play_move', game_id=game.game_key, move_id=game.move_id))
        
    def test_get_board_uris_before_save_raise_error(self):
        game = othello_model.OthelloBoardModel(6)
        with othello_restapi.app.app_context():
            with self.assertRaises(othello_model.GameNotStoredError):
                game.get_uri()
            with self.assertRaises(othello_model.GameNotStoredError):
                game.post_uri()
                
    def test_board_model_has_jsonable_function(self):
        game = othello_model.OthelloBoardModel(6)
        self.board_store.save_board(game)
        with othello_restapi.app.app_context():
            game_dict = game.get_jsonable_object()
            self.assertEqual(game_dict['URIs'], {'get': game.get_uri(), 'play': game.post_uri()})
        self.assertEqual(game_dict['game_complete'], False)
        self.assertEqual(sorted(game_dict['X']), [[2, 3],[3, 2]])
        self.assertEqual(sorted(game_dict['O']), [[2, 2],[3, 3]])
        self.assertEqual(sorted(game_dict['plays']), [[1, 2], [2, 1], [3, 4], [4, 3]])
        self.assertEqual(game_dict['current_turn'], 'X')
        self.assertEqual(game_dict['size'], 6)
        
    def test_clear_all(self):
        game = othello_model.OthelloBoardModel(6)
        self.board_store.save_board(game)
        self.board_store.clear_all()
        with self.assertRaises(othello_model.GameNotFoundError):
            self.board_store.get_board(game.game_key, game.move_id)
        
        
if __name__ == '__main__':
    unittest.main()