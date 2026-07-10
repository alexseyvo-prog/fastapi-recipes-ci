import datetime
from flask import Flask

someGlobalVar = 0
app = Flask(__name__)


@app.route('/test')
def test_function():
    now = datetime.datetime.now().utcnow()
    return f'Это тестовая страничка, ответ сгенерирован в {now}'


@app.route('/world')
def test_functionwwwww():
    global someGlobalVar
    someGlobalVar = int(someGlobalVar) + 1
    return f'Привет всем {someGlobalVar} раз'
