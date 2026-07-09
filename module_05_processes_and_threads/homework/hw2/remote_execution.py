"""
Модуль remote_execution: удалённое исполнение Python-кода с тайм-аутом.

Функциональность:
- Эндпоинт /run_code принимает код на Python (строкой) и тайм-аут в секундах.
- Код запускается в отдельном процессе через `python -c "<code>"`.
- Если выполнение уложилось в указанный тайм-аут:
    * Пользователю возвращается stdout, stderr и код возврата.
- Если выполнение не уложилось:
    * Процесс завершается.
    * Пользователь получает сообщение, что код не уложился в заданное время,
      и накопленный на этот момент stdout/stderr.

Особенности безопасности:
- Команда запуска формируется как список аргументов: ["python", "-c", code].
- Параметр shell=True НЕ используется, что защищает от командной инъекции
  на уровне оболочки (нельзя «разорвать» команду и дописать произвольные
  shell-команды).
"""

import subprocess
from dataclasses import dataclass

from flask import Flask, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

app = Flask(__name__)
# SECRET_KEY необходим Flask-WTF для защиты от CSRF в HTML-формах.
# В продакшене значение должно быть сложным и храниться в конфиге/переменных окружения.
app.config["SECRET_KEY"] = "dev-secret-key"


class CodeForm(FlaskForm):
    """
    FlaskForm для ввода Python-кода и тайм-аута.

    Поля:
    - code: строка с Python-кодом, обязательное поле, длина 1–2000 символов.
    - timeout: целое число, обязательное, от 1 до 30 секунд.
    - submit: служебная кнопка отправки формы (актуально при HTML-формах).
    """
    code = StringField(
        validators=[
            DataRequired(message="Код обязателен"),
            Length(min=1, max=2000, message="Код должен быть от 1 до 2000 символов"),
        ]
    )
    timeout = IntegerField(
        validators=[
            DataRequired(message="Тайм-аут обязателен"),
            NumberRange(min=1, max=30, message="Тайм-аут должен быть от 1 до 30 секунд"),
        ]
    )
    submit = SubmitField()


@dataclass
class RunResult:
    """
    Структура результата выполнения внешнего процесса.

    Атрибуты:
    - stdout: строка стандартного вывода процесса.
    - stderr: строка стандартного вывода ошибок процесса.
    - timed_out: True, если выполнение было прервано по тайм-ауту.
    - returncode: код возврата процесса (0 — успешное завершение),
                  может быть None, если процесс не успел корректно завершиться.
    """
    stdout: str
    stderr: str
    timed_out: bool
    returncode: int | None


def run_python_code_in_subproccess(code: str, timeout: int) -> RunResult:
    """
    Выполняет переданный Python-код в отдельном процессе с ограничением по времени.

    Запуск осуществляется командой:
        python -c "<code>"

    Параметры:
    - code: исходный текст Python-кода, который нужно выполнить.
    - timeout: максимальное время (в секундах), в течение которого
               процесс имеет право выполняться.

    Поведение:
    - Если процесс завершился до истечения тайм-аута:
        * возвращаются stdout, stderr, timed_out=False и returncode.
    - Если процесс не завершился вовремя:
        * генерируется TimeoutExpired, процесс принудительно
          завершается (kill),
        * затем дочитываются stdout/stderr,
        * возвращается результат с timed_out=True.

    Безопасность:
    - Команда задаётся списком аргументов ["python", "-c", code].
      shell=True не используется, поэтому ввод пользователя не может
      разорвать команду оболочки и выполнить дополнительные shell-команды.
    """
    # Формируем команду для запуска Python-интерпретатора.
    # ВАЖНО: используем список аргументов, а не одну строку с shell=True.
    cmd = ["python", "-c", code]

    # Открываем подпроцесс. text=True / universal_newlines=True
    # возвращают строки вместо байтов.
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        text=True,
    )

    try:
        # Ждём завершения процесса или истечения тайм-аута.
        stdout, stderr = proc.communicate(timeout=timeout)
        return RunResult(
            stdout=stdout,
            stderr=stderr,
            timed_out=False,
            returncode=proc.returncode,
        )
    except subprocess.TimeoutExpired:
        # Если процесс не уложился в timeout секунд:
        # 1) принудительно его завершаем,
        proc.kill()
        # 2) дочитываем всё, что успело накопиться в stdout/stderr.
        stdout, stderr = proc.communicate()
        return RunResult(
            stdout=stdout,
            stderr=stderr,
            timed_out=True,
            returncode=proc.returncode,
        )


@app.route('/run_code', methods=['POST'])
def run_code():
    """
    Эндпоинт /run_code: удалённое исполнение Python-кода с тайм-аутом.

    Ожидает запрос методом POST. Поддерживаются два формата входных данных:

    1. JSON:
        {
          "code": "print('Hello')",
          "timeout": 3
        }

    2. form-data / x-www-form-urlencoded (обычная HTML-форма):
        - поле "code"
        - поле "timeout"

    Логика работы:
    1. Создаётся форма CodeForm и заполняется данными из запроса.
    2. Если данные невалидны (пустой код, неверный тайм-аут и т.п.),
       возвращается ответ со статусом 400 и описанием ошибок:
        {
          "ok": false,
          "errors": {
            "code": [...],
            "timeout": [...]
          }
        }

    3. Если данные валидны:
        - вызывается run_python_code_in_subproccess(code, timeout),
        - если выполнение уложилось в тайм-аут:
            {
              "ok": true,
              "timed_out": false,
              "stdout": "...",
              "stderr": "...",
              "returncode": 0
            }
        - если выполнение не уложилось:
            {
              "ok": false,
              "timed_out": true,
              "message": "Исполнение кода не уложилось в N секунд(ы)",
              "stdout": "...",
              "stderr": "..."
            }

    Примечание:
    - Эндпоинт не выполняет дополнительную «песочницу» для кода.
      Код исполняется тем Python-интерпретатором, из которого запущено приложение,
      поэтому доверять ему можно только в учебных/контролируемых сценариях.
    """
    form = CodeForm()

    # Поддержка JSON-запросов: если запрос JSON и поля формы ещё не заполнены,
    # берём данные из тела JSON вручную.
    if request.is_json and not form.code.data:
        data = request.get_json(silent=True) or {}
        form.code.data = data.get("code")
        form.timeout.data = data.get("timeout")

    # Проверяем данные формы: типы, диапазоны, обязательность.
    if not form.validate():
        # Некорректные данные — возвращаем ошибки валидации.
        return jsonify({
            "ok": False,
            "errors": form.errors,
        }), 400

    # Если данные валидны, извлекаем их.
    code = form.code.data
    timeout = form.timeout.data

    # Запускаем код в подпроцессе с ограничением по времени.
    result = run_python_code_in_subproccess(code, timeout)

    if result.timed_out:
        # Случай, когда код не уложился в тайм-аут.
        return jsonify({
            "ok": False,
            "timed_out": True,
            "message": f"Исполнение кода не уложилось в {timeout} секунд(ы)",
            "stdout": result.stdout,
            "stderr": result.stderr,
        }), 200

    # Случай успешного завершения до истечения тайм-аута.
    return jsonify({
        "ok": True,
        "timed_out": False,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }), 200


if __name__ == '__main__':
    # Запуск Flask-приложения в режиме разработки.
    # В продакшене следует использовать специализированный WSGI-сервер (gunicorn, uWSGI и т.п.).
    app.run(debug=True)