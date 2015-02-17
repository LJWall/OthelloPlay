#! /usr/bin/env python3

import othello_restapi
import unittest
from flask.json import loads as json_loads

class OthelloRestAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = othello_restapi.app.test_client()
        
    def test_404_error(self):
        response = self.app.get('/no/such/URI')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.mimetype, 'application/json')
    
    
if __name__ == '__main__':
    unittest.main()
