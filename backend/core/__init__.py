from flask import Flask, jsonify, request
from flask_cors import CORS

from .server import BackendManager

from .tools import tag_post

serverManager = BackendManager()

app = Flask(__name__)
CORS(app)

@app.route("/analyse_post", methods=["GET", "POST"])
def analyse_post():
    try:
        post_body = request.get_json()["post_body"]
        return jsonify(tag_post(post_body)), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Bad request"}), 400