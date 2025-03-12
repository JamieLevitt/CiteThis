from flask import Flask, request, jsonify, url_for
from dataclasses import asdict

from .server import ServerManager

serverManager = ServerManager()

app = Flask(__name__)

app.route('/')
def index():
    return jsonify(url_for("analyse_post"))

app.route('/analyse_post', methods = ["GET", "POST"])
def analyse_post():
    return jsonify([asdict(topic) for topic in serverManager.load_topics()]), 200