import json
from flask import Flask, request

app = Flask(__name__)
logs_storage = []


@app.route('/log', methods=['POST'])
def log():
    """
    Принимаем один лог или список логов, записываем в память.
    """
    # HTTPHandler по умолчанию шлёт form-поля, читаем их так:
    data = request.form.to_dict()  # {'name': 'app', 'levelname': 'INFO', 'msg': '...', ...}

    logs_storage.append(data)

    print("Received log:", data)  # для отладки
    return 'log received', 200


@app.route('/logs', methods=['GET'])
def logs():
    return f"<pre>{json.dumps(logs_storage, ensure_ascii=False, indent=2)}</pre>", 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)