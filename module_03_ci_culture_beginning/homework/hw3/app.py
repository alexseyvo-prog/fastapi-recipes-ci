from flask import Flask, request

# Импортируем Flask и объект request.
# Flask используется для создания веб-приложения и определения маршрутов.
# request нужен, чтобы читать параметры из HTTP-запроса (GET-параметры в строке запроса).


app = Flask(__name__)
# Создаём экземпляр Flask-приложения.
# Переменная app представляет собой веб-сервер, который будет обрабатывать запросы.


storage = {}
# Глобальный словарь storage.
# В нём мы храним все данные о доходах.
# Структура:
# {
#     'YYYYMMDD': {
#         'category1': amount1,
#         'category2': amount2,
#         ...
#     },
#     ...
# }


def add_income(date: str, amount: int, category: str) -> None:
    """
    Добавляет доход в хранилище storage по указанной дате и категории.

    Параметры:
    - date: строка с датой в формате 'YYYYMMDD' (ровно 8 цифр).
    - amount: сумма дохода (целое число).
    - category: категория дохода (строка).

    Логика:
    - проверяем, что дата состоит из 8 символов и все они цифры,
      иначе выбрасываем TypeError('Invalid date format');
    - если для этой даты ещё нет записи в storage, создаём пустой словарь;
    - увеличиваем сумму по нужной категории: к текущему значению (или 0, если категории ещё нет)
      прибавляем amount.
    """
    if len(date) != 8 or not date.isdigit():
        raise TypeError('Invalid date format')

    if date not in storage:
        storage[date] = {}

    storage[date][category] = storage[date].get(category, 0) + amount


def calculate_all() -> int:
    """
    Возвращает общую сумму всех доходов за все даты и категории.

    Логика:
    - проходим по всем значениям словаря storage (это словари по датам);
    - для каждого словаря дат суммируем все значения (суммы по категориям);
    - складываем эти суммы в переменную total и возвращаем её.
    """
    total = 0
    for date_data in storage.values():
        total += sum(date_data.values())
    return total


def calculate_by_date(date: str) -> int:
    """
    Возвращает сумму доходов только за указанную дату.

    Логика:
    - берём словарь по нужной дате через storage.get(date, {}),
      если такой даты нет — используем пустой словарь;
    - суммируем все значения (суммы по категориям) и возвращаем результат.
    """
    return sum(storage.get(date, {}).values())


def calculate_by_category(category: str) -> int:
    """
    Возвращает сумму доходов по указанной категории за все даты.

    Логика:
    - проходим по всем датам (значениям storage);
    - для каждой даты берём сумму по нужной категории через date_data.get(category, 0);
    - добавляем эти суммы в общий total и возвращаем его.
    """
    total = 0
    for date_data in storage.values():
        total += date_data.get(category, 0)
    return total


@app.route('/add/')
def add_endpoint():
    """
    HTTP-эндпоинт /add/, который добавляет доход на основании GET-параметров запроса.

    Ожидаемые параметры:
    - date: строка даты в формате 'YYYYMMDD';
    - amount: сумма дохода (строка, преобразуется в int);
    - category: категория дохода.

    Логика:
    - получаем параметры из request.args (строка запроса);
    - преобразуем amount в целое число;
    - вызываем add_income(date, amount, category) для записи данных в storage;
    - возвращаем строку 'OK' в качестве простого подтверждения.
    """
    date = request.args.get('date')
    amount = int(request.args.get('amount'))
    category = request.args.get('category')
    add_income(date, amount, category)
    return 'OK'


@app.route('/calculate/')
def calculate_endpoint():
    """
    HTTP-эндпоинт /calculate/, который возвращает сумму доходов.

    Ожидаемые GET-параметры (необязательные):
    - date: если указан, считается сумма только за эту дату;
    - category: если указана, считается сумма только по этой категории за все даты.

    Логика:
    - если передан параметр date, вызываем calculate_by_date(date) и возвращаем результат;
    - иначе, если передан параметр category, вызываем calculate_by_category(category);
    - если ни date, ни category не переданы, возвращаем общую сумму через calculate_all();
    - результат всегда преобразуется в строку перед отправкой клиенту.
    """
    date = request.args.get('date')
    category = request.args.get('category')

    if date:
        return str(calculate_by_date(date))
    if category:
        return str(calculate_by_category(category))
    return str(calculate_all())


if __name__ == '__main__':
    # Запускаем Flask-приложение в режиме отладки.
    # debug=True включает подробные сообщения об ошибках и автоматическую перезагрузку
    # при изменении кода. Используется только в разработке, не в продакшене.
    app.run(debug=True)