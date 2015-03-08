#! /usr/bin/env python3
import othello.othello_restapi as othello_restapi
import othello.othello_model as othello_model
from othello.ml.strategies import strategies
import unittest
from flask.json import loads as json_loads, dumps as json_dumps
from flask import url_for
import pickle


othello_restapi.app.config.update(
    {'DATABASE_USER': 'unittester',
    'DATABASE_PASSWORD': 'unittester',
    'DATABASE_NAME': 'othello_unittest',
    'DATABASE_HOST': '127.0.0.1',
    'TESTING': True,
    'SERVER_NAME': 'localhost'})
          
class OthelloRestAPITestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.board_store = othello_model.BoardStore()
    
    @classmethod
    def tearDownClass(cls):
        cls.board_store.clear_all()
    
    def setUp(self):
        self.board_store.clear_all()
        self.app = othello_restapi.app.test_client()
        
    def test_404_error(self):
        response = self.app.get('/no/such/URI')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, 'text/html')
        
    def test_get_game(self):
        game = othello_model.OthelloBoardModel(6)
        game.play_move(2, 1) # make a play first, just to make it slightly less vanilla
        self.board_store.save_board(game)
        with othello_restapi.app.app_context():
            response = self.app.get(game.get_uri())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        game_data = json_loads(response.data)
        with othello_restapi.app.app_context():
            self.assertEqual(game_data, game.get_jsonable_object())
        
    def test_get_game_bad_id_gives_404(self):
        response = self.app.get('/game/NoSuchGame/0')
        self.assertEqual(response.status_code, 404)
    
    def test_get__api_root(self):
        response = self.app.get('/game')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(json_loads(response.data), strategies.get_jsonable_object())
        
    def test_game_post_play_move(self):
        game = othello_model.OthelloBoardModel(6)
        self.board_store.save_board(game)
        # play a move on the server end by posting
        with othello_restapi.app.app_context():
            response = self.app.post(game.post_uri(), data=json_dumps({'play': [1, 2]}), content_type='application/json')
        # confirm correct response headers
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        with othello_restapi.app.app_context():
            self.assertRegex(response.headers['Location'], url_for('get_game', game_id=game.game_key, move_id=1) + '$')
        game_data = json_loads(response.data)
        # confirm response data by playing move in our local obejct (and update the IDs as we expect the api to do)...
        game.play_move(1, 2)
        game.move_id = 1
        game.last_move_id = 0
        with othello_restapi.app.app_context():
            self.assertEqual(game_data, game.get_jsonable_object())
    
    def test_game_post_autoplay_move(self):
        game = othello_model.OthelloBoardModel(6)
        self.board_store.save_board(game)
        with othello_restapi.app.app_context():
            response = self.app.post(game.post_uri(), data=json_dumps({'play': 'auto'}), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        with othello_restapi.app.app_context():
            self.assertRegex(response.headers['Location'], url_for('get_game', game_id=game.game_key, move_id=1) + '$')
        game_data = json_loads(response.data)
        # check a move has been made
        with othello_restapi.app.app_context():
            self.assertNotEqual(game.get_jsonable_object()['board'], game_data['board'])
        self.assertEqual(game_data['current_turn'], 'O')    
        
    def test_game_play_invalid_move_gives_400(self):
        game = othello_model.OthelloBoardModel(6)
        self.board_store.save_board(game)
        with othello_restapi.app.app_context():
            response = self.app.post(game.post_uri(), data=json_dumps({'play': [2, 2]}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json_loads(response.data)['error'], '<p>Invalid move</p>')
        with othello_restapi.app.app_context():
            response = self.app.post(game.post_uri(), data=json_dumps({'play': [2, 6]}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json_loads(response.data)['error'], '<p>Invalid move</p>')
    
    def test_post_game_returns_201(self):
        response = self.app.post('/game', data=json_dumps({'game_size': 8}), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
    def test_post_game_return_400_on_non_positve_game_size(self):
        response = self.app.post('/game', data=json_dumps({'game_size': 3}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json_loads(response.data)['error'], '<p>game_size should be at least four</p>')
        
    def test_post_game_return_400_on_missing_game_size(self):
        response = self.app.post('/game', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json_loads(response.data)['error'], '<p>game_size not specified</p>')
    
    def test_post_game_actualy_creates_game(self):
        response = self.app.post('/game', data=json_dumps({'game_size': 12}), content_type='application/json')
        uri_split = response.headers['Location'].split('/')
        game = self.board_store.get_board(uri_split[-2], int(uri_split[-1]))
        # the following should pass, even theough the object will not be the same (e.g. the former
        # will contain game_key/move_id info), they are the same as dictionaries
        self.assertDictEqual(game, othello_model.OthelloBoardModel(12))
        
    def test_post_game_returns_same_data_as_subsequent_get(self):
        response_post = self.app.post('/game', data=json_dumps({'game_size': 8}), content_type='application/json')
        response_get = self.app.get(response_post.headers['Location'])
        self.assertEqual(json_loads(response_post.data), json_loads(response_get.data))
        
    def test_play_move_doesnt_lose_previous_data(self):
        response_post = self.app.post('/game', data=json_dumps({'game_size': 6}), content_type='application/json')
        data0 = json_loads(response_post.data)
        response_playmove = self.app.post(data0['URIs']['play'], data=json_dumps({'play': [1, 2]}), content_type='application/json')
        data1 = json_loads(response_playmove.data)
        self.assertNotEqual(data0, data1)
        response_get0 = self.app.get(response_post.headers['Location'])
        response_get1 = self.app.get(response_playmove.headers['Location'])
        self.assertEqual(data0, json_loads(response_get0.data))
        self.assertEqual(data1, json_loads(response_get1.data))
        
        
        
        
    
if __name__ == '__main__':
    unittest.main()
