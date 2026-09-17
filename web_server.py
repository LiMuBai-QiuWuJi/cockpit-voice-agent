import os
import json
import main
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from main import cloud_handle
from domains import car_state

app = Flask(__name__)
CORS(app)

script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, ".env"))


@app.route("/")
def index():
    return send_from_directory(script_dir, "index.html")


@app.route("/api/mode", methods=["GET", "POST"])
def mode():
    if request.method == "POST":
        data = request.get_json() or {}
        main.USE_ONLINE_LLM = bool(data.get("online", True))
    return jsonify({"online": main.USE_ONLINE_LLM})


@app.route("/api/state", methods=["GET"])
def get_state():
    return jsonify(car_state)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    user_input = data.get("user_input", "")
    current_state = data.get("car_state", car_state)

    payload = json.dumps(
        {"user_input": user_input, "car_state": current_state},
        ensure_ascii=False,
    )
    reply_json = cloud_handle(payload=payload)
    reply = json.loads(reply_json)

    return jsonify({
        "say": reply.get("say", ""),
        "actions": reply.get("actions", []),
        "car_state": car_state,
        "online": main.USE_ONLINE_LLM,
    })


if __name__ == "__main__":
    print("启动车载语音中台 Web 服务：http://127.0.0.1:5000")
    print("打开浏览器访问：http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
