#! /usr/bin/env python3

from flask import Flask, jsonify, abort, make_response, request, url_for, g
import mysql.connector
import pickle
import othello
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
    if not getattr(g, 'db_conn', None):
        g.db_conn = mysql.connector.connect(user=app.config['DATABASE_USER'],
                                            password=app.config['DATABASE_PASSWORD'],
                                            database=app.config['DATABASE_NAME'],
                                            host=app.config['DATABASE_HOST'])
    
@app.after_request
def disconnect_db(response):
    if getattr(g, 'db_conn', None):
        g.db_conn.close()
    return response

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

@app.route('/game/<game_id>', methods = ['PUT'])
def play_move(game_id):
    pass

@app.route('/game/<game_id>', methods = ['GET'])
def get_game(game_id):
    cur = g.db_conn.cursor()
    cur.execute('select `value` from othello_data where `key`=%s', (game_id, ))
    results = cur.fetchall()
    if len(results):
        game = pickle.loads(results[0][0])
        game_dict = make_game_jsonable(game)
        game_dict['play_uri'] = url_for('play_move', game_id=game_id)
        return jsonify(game_dict)
    else:
        abort(404)
    
    
if __name__ == "__main__":
    app.run()