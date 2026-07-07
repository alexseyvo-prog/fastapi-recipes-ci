# uptime.py

import os
from flask import Flask

app = Flask(__name__)


@app.route("/uptime", methods=["GET"])
def uptime() -> str:
    raw = os.popen("uptime -p").read().strip()
    prefix = "up "
    uptime_str = raw[len(prefix):] if raw.startswith(prefix) else raw
    return f"Current uptime is {uptime_str}"


if __name__ == "__main__":
    # ВАЖНО: app.run вызывается только при запуске файла напрямую,
    # а НЕ при импорте (когда pytest делает `from uptime import app`)
    app.run(debug=True)