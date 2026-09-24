import time

from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify(
        message="Application is working",
        endpoint="/long_task",
    )


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/long_task")
def long_task():
    time.sleep(300)
    return jsonify(message="We did it!")