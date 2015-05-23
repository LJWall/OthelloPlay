#! /usr/bin/env python3

from flask import Flask, jsonify, make_response, request, g, render_template, redirect, url_for
from flask.json import loads as json_loads
from werkzeug.exceptions import NotFound, BadRequest
from othello.ml.strategies import strategies
import pickle
from othello.othello import GameCompleteError, InvalidMoveError, NoAvailablePlayError
app = Flask(__name__, template_folder='static')

import othello.othello_model as othello_model

app.config.from_pyfile('config.cfg')

@app.before_request
def connect_db():
    if request.method in ('POST') and  'application/json' not in request.headers['Content-Type'].lower():
        raise BadRequest('Invlalid content type')
    if not  getattr(g, 'board_store', None):
        g.board_store = othello_model.BoardStore()

@app.errorhandler(404)
def not_found(error):
    return make_response(render_template('error404.html', url_home=url_for('home', _external=True)), 404)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': error.get_description()}), 400)

@app.route('/fonts/<font_file>', methods = ['GET'])
def font_redir(font_file):
    return redirect(url_for('static', filename=font_file))

@app.route('/', methods = ['GET'])
def home():
    #return redirect(url_for('static', filename='index.html'))
    return render_template('index.html')

@app.route('/game', methods = ['GET'])
def start_info():
    response = jsonify(strategies.get_jsonable_object())
    return response


@app.route('/game', methods = ['POST'])
def create_game():
    try:
        game_size = int(json_loads(request.data)['game_size'])
    except BaseException:
        raise BadRequest('game_size not specified')
    if game_size<4:
        raise BadRequest('game_size should be at least four')
    game = othello_model.OthelloBoardModel(game_size)
    g.board_store.save_board(game)
    response = jsonify(game.get_jsonable_object())
    response.headers['Location'] = game.get_uri()
    response.status_code = 201
    return response

@app.route('/game/<game_id>/<int:move_id>', methods = ['POST'])
def play_move(game_id, move_id):
    try:
        game = g.board_store.get_board(game_id, move_id)
    except othello_model.GameNotFoundError:
        raise NotFound('Game not found.')
    # Attempt to interpret and carry out the request
    try:
        data = json_loads(request.data)
        play = data['play']
    except BaseException:
        raise BadRequest('Unable to interpret request')
    if play == 'auto':
        strategy_name = None
        if 'strategy' in data:
            strategy_name = data['strategy']
            if strategy_name not in strategies:
                raise BadRequest('Unknown strategy')
        try:
            if strategy_name:
                strategies[strategy_name](game)
            else:
                game.auto_play_move()
        except NoAvailablePlayError:
            raise BadRequest('No available plays')
        except GameCompleteError:
            raise BadRequest('Game complete')
    else:
        try:
            play = (int(play[0]), int(play[1]))
        except BaseException:
            raise BadRequest('Unable to interpret request')    
        try:
            game.play_move(*play)
        except InvalidMoveError:
            raise BadRequest('Invalid move')
        except GameCompleteError:
            raise BadRequest('Game complete')
    g.board_store.save_board(game)
    response = jsonify(game.get_jsonable_object())
    response.headers['Location'] = game.get_uri()
    response.status_code = 201
    return response
    
@app.route('/game/<game_id>/<int:move_id>', methods = ['GET'])
def get_game(game_id, move_id):
    try:
        game = g.board_store.get_board(game_id, move_id)
    except othello_model.GameNotFoundError:
        raise NotFound('Game not found.')
    return jsonify(game.get_jsonable_object())
