import pickle
import pymongo
import othello.othello as othello
from othello.othello import GameCompleteError, InvalidMoveError, NoAvailablePlayError
from othello.othello_restapi import app
from random import randint
from flask import url_for

class GameNotFoundError(BaseException):
    pass

class GameAlreadyStoredError(BaseException):
    pass

class GameNotStoredError(BaseException):
    pass

class BoardStore():
    def __init__(self):
        self.db_conn = pymongo.MongoClient(app.config['DATABASE_URI'])
        self.collection = self.db_conn.Othello_unittest.board_data
        
    def __del__(self):
        if getattr(self, 'db_conn', None):
            self.db_conn.close()
         
    def clear_all(self):
        self.collection.delete_many({})
    
    
    def get_board(self, game_key, move_id):
        result = self.collection.find_one_and_update({'game_key': game_key, 'move_id': move_id}, {'$currentDate': {'last_hit': {'$type': "timestamp"}}})
        if result is None:
            raise GameNotFoundError
        return pickle.loads(result['game'])
        
        
        
    def save_board(self, board):
        if board.game_key is not None and board.move_id is not None:
            raise GameAlreadyStoredError
        if board.game_key is None:
            results = self.collection.find({}, ['game_key']).distinct('game_key')
            game_key = randint(1000000, 9999999)
            while game_key in results:
                game_key = randint(1000000, 9999999)
            board.move_id = 0
            board.game_key = str(game_key)
        else:
            results = self.collection.find({'game_key': board.game_key}, ['move_id'], limit=1, sort=[('move_id', pymongo.DESCENDING)])
            if results.count() > 0:
                board.move_id = results[0]['move_id']+1
            else:
                # arrive here if saving a board for which game_key is already set, yet
                # no matching games found stroed in the db - this indicates an error
                raise GameNotFoundError
        self.collection.insert_one({'game_key': board.game_key, 'move_id': board.move_id, 'game': pickle.dumps(board)});
                    

class OthelloBoardModel(othello.OthelloBoardClass):
    game_key = None
    move_id = None
    last_move_id = None
    
    def play_move(self, x, y, test_only=False):
        result = super().play_move(x, y, test_only)
        if not test_only:
            self.last_move_id = self.move_id
            self.move_id = None
        return result
        
    def get_uri(self):
        if self.game_key is None or self.move_id is None:
            raise GameNotStoredError
        return url_for('get_game', game_id=self.game_key, move_id=self.move_id, _external=False)
    
    def post_uri(self):
        if self.game_key is None or self.move_id is None:
            raise GameNotStoredError
        return url_for('play_move', game_id=self.game_key, move_id=self.move_id, _external=False)
    
    def get_jsonable_object(self, shallow=False):
        game_dict = dict()
        game_dict['board'] = []
        for x in range(self.size):
            game_dict['board'].append(['']*self.size)
        for key in self:
            game_dict['board'][key[0]][key[1]] = self[key]
        game_dict['current_turn'] = self.current_turn
        game_dict['game_complete'] = self.game_complete
        if not shallow:
            play_results = self.get_plays(simple=False)
            for play in play_results:
                game_dict['board'][play[0]][play[1]] = 'P'
            game_dict['playresults'] = {str(play): play_results[play].get_jsonable_object(shallow=True) for play in play_results}
            game_dict['URIs'] = {'get': self.get_uri()}
            if not self.game_complete:
                game_dict['URIs']['play'] = self.post_uri()
        return game_dict
        
    
    