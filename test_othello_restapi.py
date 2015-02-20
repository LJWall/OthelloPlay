#! /usr/bin/env python3
import othello_restapi
import othello
import unittest
from flask.json import loads as json_loads, dumps as json_dumps
import mysql.connector
import pickle


othello_restapi.app.config.update(
    {'DATABASE_USER': 'unittester',
    'DATABASE_PASSWORD': 'unittester',
    'DATABASE_NAME': 'othello_unittest',
    'DATABASE_HOST': '127.0.0.1',
    'TESTING': True})
          
class OthelloRestAPITestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.db_conn = mysql.connector.connect(user='unittester',
                                            password='unittester',
                                            database='othello_unittest',
                                            host='127.0.0.1',
                                            autocommit=True)
    
    @classmethod
    def teadDownClass(cls):
        if getattr(cls, dn_conn, None):
            self.db_conn.cmd_query('DELETE FROM othello_data;')    
            cls.dn_conn.close()
    
    def setUp(self):
        self.db_conn.cmd_query('DELETE FROM othello_data;')
        self.app = othello_restapi.app.test_client()
        
    def test_404_error(self):
        response = self.app.get('/no/such/URI')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, 'application/json')
    
    def add_blank_game(self, size):
        game = othello.OthelloBoardClass(size)
        cur = self.db_conn.cursor()
        cur.execute('INSERT INTO othello_data (`key`, `value`) VALUES (%s, %s)', ('test', pickle.dumps(game)))
        
    def test_get_game(self):
        self.add_blank_game(6)
        response = self.app.get('/game/test')
        game_data = json_loads(response.data)
        self.assertEqual(sorted(game_data['X']), [[2, 3],[3, 2]])
        self.assertEqual(sorted(game_data['O']), [[2, 2],[3, 3]])
        self.assertEqual(sorted(game_data['plays']), [[1, 2], [2, 1], [3, 4], [4, 3]])
        self.assertEqual(game_data['current_turn'], 'X')
        self.assertEqual(game_data['size'], 6)
        self.assertEqual(game_data['play_uri'], '/game/test')
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        
    def test_get_game_bad_id_gives_404(self):
        response = self.app.get('/game/NoSuchGame')
        self.assertEqual(response.status_code, 404)
        
        
    def test_game_put_play_move(self):
        self.add_blank_game(6)
        response = self.app.put('/game/test', data=json_dumps({'play': [1, 2]}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        game_data = json_loads(response.data)
        self.assertEqual(sorted(game_data['X']), [[1, 2], [2, 2], [2, 3],[3, 2]])
        self.assertEqual(sorted(game_data['O']), [[3, 3]])
        self.assertEqual(sorted(game_data['plays']), [[1, 1], [1, 3], [3, 1]])
        self.assertEqual(game_data['current_turn'], 'O')
        self.assertEqual(game_data['size'], 6)
        self.assertEqual(game_data['play_uri'], '/game/test')
            
        
    def test_game_play_invalid_move_gives_400(self):
        self.add_blank_game(6)
        response = self.app.put('/game/test', data=json_dumps({'play': [2, 2]}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual('<p>Invlalid move</p>', json_loads(response.data)['error'])
        response = self.app.put('/game/test', data=json_dumps({'play': [2, 6]}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual('<p>Invlalid move</p>', json_loads(response.data)['error'])
    
    def test_post_game_returns_201_plus_header(self):
        response = self.app.post('/game', data=json_dumps({'game_size': 8}), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        
    def test_post_game_return_400_on_non_positve_game_size(self):
        response = self.app.post('/game', data=json_dumps({'game_size': 3}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual('<p>game_size should be at least four</p>', json_loads(response.data)['error'])
        
    def test_post_game_return_400_on_missing_game_size(self):
        response = self.app.post('/game', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual('<p>game_size not specified</p>', json_loads(response.data)['error'])
    
    def test_post_game_actualy_creates_game(self):
        response = self.app.post('/game', data=json_dumps({'game_size': 12}), content_type='application/json')
        cur = self.db_conn.cursor()
        cur.execute('SELECT `value` from othello_data where `key`=%s', (response.headers['Location'].split('/')[-1],))
        result = cur.fetchall()
        game = pickle.loads(result[0][0])
        self.assertEqual(game, othello.OthelloBoardClass(12))
        
    def test_post_game_returns_same_data_as_subsequent_get(self):
        response_post = self.app.post('/game', data=json_dumps({'game_size': 8}), content_type='application/json')
        response_get = self.app.get(response_post.headers['Location'])
        self.assertEqual(json_loads(response_post.data), json_loads(response_get.data))
        
    
if __name__ == '__main__':
    unittest.main()
