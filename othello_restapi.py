#! /usr/bin/env python3

from flask import Flask, jsonify, abort, make_response, request, url_for

app = Flask(__name__)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

    
if __name__ == "__main__":
    app.run()