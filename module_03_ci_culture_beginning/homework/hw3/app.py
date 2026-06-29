from flask import Flask, request

app = Flask(__name__)

storage = {}


def add_income(date: str, amount: int, category: str) -> None:
    if len(date) != 8 or not date.isdigit():
        raise TypeError('Invalid date format')

    if date not in storage:
        storage[date] = {}

    storage[date][category] = storage[date].get(category, 0) + amount


def calculate_all() -> int:
    total = 0
    for date_data in storage.values():
        total += sum(date_data.values())
    return total


def calculate_by_date(date: str) -> int:
    return sum(storage.get(date, {}).values())


def calculate_by_category(category: str) -> int:
    total = 0
    for date_data in storage.values():
        total += date_data.get(category, 0)
    return total


@app.route('/add/')
def add_endpoint():
    date = request.args.get('date')
    amount = int(request.args.get('amount'))
    category = request.args.get('category')
    add_income(date, amount, category)
    return 'OK'


@app.route('/calculate/')
def calculate_endpoint():
    date = request.args.get('date')
    category = request.args.get('category')

    if date:
        return str(calculate_by_date(date))
    if category:
        return str(calculate_by_category(category))
    return str(calculate_all())


if __name__ == '__main__':
    app.run(debug=True)