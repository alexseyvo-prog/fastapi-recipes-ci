"""
Напишите GET-эндпоинт /ps, который принимает на вход аргументы командной строки,
а возвращает результат работы команды ps с этими аргументами.
Входные значения эндпоинт должен принимать в виде списка через аргумент arg.

Например, для исполнения команды ps aux запрос будет следующим:

/ps?arg=a&arg=u&arg=x
"""

import shlex
import subprocess
from typing import List

from flask import Flask, request

app = Flask(__name__)


@app.route("/ps", methods=["GET"])
def ps() -> str:
    """
    Эндпоинт /ps:
    - получает все значения query-параметра 'arg' списком;
      например, /ps?arg=a&arg=u&arg=x -> ['a', 'u', 'x']
    - экранирует каждый аргумент с помощью shlex.quote для защиты от инъекций;
    - собирает команду ['ps', <аргументы>];
    - выполняет её через subprocess.run и возвращает stdout в теге <pre>...</pre>.
    """
    # Получаем список аргументов из строки запроса
    args: List[str] = request.args.getlist("arg")

    # Экранируем каждый пользовательский аргумент
    safe_args = [shlex.quote(arg) for arg in args]

    # Формируем команду: ps + аргументы
    command = ["ps"] + safe_args

    # Запускаем команду и захватываем вывод
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    # Берём stdout; в случае ошибки можно при желании добавить stderr
    output = result.stdout

    # Возвращаем красиво отформатированный результат
    return f"<pre>{output}</pre>"


if __name__ == "__main__":
    app.run(debug=True)