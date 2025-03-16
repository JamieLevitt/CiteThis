from flask import Flask, current_app, jsonify

from .server import ServerManager
from .tools import analyse_post
from structs.data import TrendStruct

serverManager = ServerManager()

app = Flask(__name__)


@app.route("/analyse_post") #, methods = ["GET", "POST"])
def analyse_post():
    #return jsonify(analyse_post(request.get_json["post_body"])), 200
    return jsonify(TrendStruct.load_all_with_meta()), 200

@app.route("/")
def index():
    current_app.logger.info("hello")
    return jsonify("hello"), 200