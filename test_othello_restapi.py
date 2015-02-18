#! /usr/bin/env python3

import othello_restapi
import unittest
from flask.json import loads as json_loads
from flask import appcontext_pushed, appcontext_popped, appcontext_tearing_down, signals_available, request_started

            
class OthelloRestAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = othello_restapi.app.test_client()
        
    def test_404_error(self):
        response = self.app.get('/no/such/URI')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, 'application/json')
        
    def test_root_URI(self):
        response = self.app.get('/')
        print(response.data)
    
    
if __name__ == '__main__':
    unittest.main()
