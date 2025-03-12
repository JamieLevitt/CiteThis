from flask import Flask, request, jsonify

from .server import ServerManager
from .tools import analyse_post

serverManager = ServerManager()

app = Flask(__name__)

app.route('/analyse_post', methods = ["GET", "POST"])
def analyse_post():
    return jsonify(analyse_post(request.get_json["post_body"])), 200
