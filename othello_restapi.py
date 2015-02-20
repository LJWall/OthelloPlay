#! /usr/bin/env python3

from flask import Flask, jsonify, make_response, request, url_for, g
from flask.json import loads as json_loads
from werkzeug.exceptions import NotFound, BadRequest
import mysql.connector
import pickle
import othello
from random import randint
app = Flask(__name__)

app.config['DATABASE_USER'] = 'othello'
app.config['DATABASE_PASSWORD'] = 'othello'
app.config['DATABASE_NAME'] = 'Othello'
app.config['DATABASE_HOST'] = '127.0.0.1'


def make_game_jsonable(game):
    game_dict = dict()
    game_dict['X'] = [key for key in game if game[key]=='X']
    game_dict['O'] = [key for key in game if game[key]=='O']
    game_dict['current_turn'] = game.current_turn
    game_dict['plays'] = list(othello.get_plays(game).keys())
    game_dict['size'] = game.size
    return game_dict

@app.before_request
def connect_db():
    if request.method in ('POST', 'PUT') and request.headers['Content-Type'] != 'application/json':
        raise BadRequest('Invlalid content type')
    if not getattr(g, 'db_conn', None):
        g.db_conn = mysql.connector.connect(user=app.config['DATABASE_USER'],
                                            password=app.config['DATABASE_PASSWORD'],
                                            database=app.config['DATABASE_NAME'],
                                            host=app.config['DATABASE_HOST'],
                                            autocommit=True)
    
    
@app.after_request
def disconnect_db(response):
    if getattr(g, 'db_conn', None):
        g.db_conn.close()
    return response

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': error.get_description()}), 404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': error.get_description()}), 400)

@app.route('/game', methods = ['POST'])
def create_game():
    try:
        game_size = int(json_loads(request.data)['game_size'])
    except BaseException:
        raise BadRequest('game_size not specified')
    if game_size<4:
        raise BadRequest('game_size should be at least four')
    game = othello.OthelloBoardClass(game_size)
    cur = g.db_conn.cursor()
    cur.execute('select `key` from othello_data')
    keys = cur.fetchall()
    game_key = randint(10000, 99999)
    while (game_key, ) in keys:
        game_key = randint(10000, 99999)
    cur.execute('insert into othello_data (`key`, `value`) values (%s, %s)', (str(game_key), pickle.dumps(game)))
    game_dict = make_game_jsonable(game)
    game_dict['play_uri'] = url_for('play_move', game_id=game_key)
    response = jsonify(game_dict)
    response.headers['Location'] = '/game/' + str(game_key)
    response.status_code = 201
    return response

@app.route('/game/<game_id>', methods = ['PUT'])
def play_move(game_id):
    # get the game from the db store
    cur = g.db_conn.cursor()
    cur.execute('select `value` from othello_data where `key`=%s', (game_id, ))
    results = cur.fetchall()
    if not len(results):
        raise NotFound('Game not found.')
    game = pickle.loads(results[0][0])
    # Attempt to interpret and carry out the request
    try:
        play = json_loads(request.data)['play']
    except BaseException:
        raise BadRequest('Unable to interpret request')
    if play == 'auto':
        try:
            othello.auto_play_move(game)
        except othello.NoAvailablePlayError:
            raise BadRequest('No available plays')
    else:
        try:
            play = (int(play[0]), int(play[1]))
        except BaseException:
            raise BadRequest('Unable to interpret request')    
        try:
            game.play_move(*play)
        except othello.InvalidMoveError:
            raise BadRequest('Invlalid move')
    
    cur.execute('update othello_data set `last_hit`=NOW(6), `value`=%s where `key`=%s', (pickle.dumps(game), game_id))
    game_dict = make_game_jsonable(game)
    game_dict['play_uri'] = url_for('play_move', game_id=game_id)
    return jsonify(game_dict)
        
    
@app.route('/game/<game_id>', methods = ['GET'])
def get_game(game_id):
    cur = g.db_conn.cursor()
    cur.execute('update othello_data set `last_hit`=NOW(6) where `key`=%s', (game_id, ))
    cur.execute('select `value` from othello_data where `key`=%s', (game_id, ))
    results = cur.fetchall()
    if len(results):
        game = pickle.loads(results[0][0])
        game_dict = make_game_jsonable(game)
        game_dict['play_uri'] = url_for('play_move', game_id=game_id)
        return jsonify(game_dict)
    else:
        raise NotFound('Game not found.')
    
    
if __name__ == "__main__":
    app.run()