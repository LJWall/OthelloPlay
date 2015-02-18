#! /usr/bin/env python3

from flask import Flask, jsonify, abort, make_response, request, url_for, g
import mysql.connector

app = Flask(__name__)

app.config['DATABASE_USER'] = 'othello'
app.config['DATABASE_PASSWORD'] = 'othello'
app.config['DATABASE_NAME'] = 'Othello'
app.config['DATABASE_HOST'] = '127.0.0.1'

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

@app.route('/', methods = ['GET'])
def root_URI():
    cur = g.db_conn.cursor()
    cur.execute('select `key`, `value` from othello_data;')
    results = cur.fetchall()
    return jsonify({row[0]: str(row[1]) for row in results})
    
    
if __name__ == "__main__":
    app.run()