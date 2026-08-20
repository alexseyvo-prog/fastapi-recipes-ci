import re
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).parent
DATABASE_PATH = BASE_DIR / 'hw.db'
SQL_PATH = BASE_DIR / 'queries.sql'


def read_queries(sql_text):
    pattern = r'--\s*RESULT:\s*(\d+)\s*\n(.*?)(?=--\s*RESULT:|\Z)'
    matches = re.findall(pattern, sql_text, flags=re.DOTALL)

    queries = []

    for number, query in matches:
        query = re.sub(
            r'^--.*$',
            '',
            query,
            flags=re.MULTILINE
        ).strip()

        if query:
            queries.append((number, query))

    return queries


def print_result(connection, number, query):
    print(f'\n{"=" * 70}')
    print(f'РЕЗУЛЬТАТ ЗАПРОСА {number}')
    print('=' * 70)

    cursor = connection.execute(query)

    column_names = [
        description[0]
        for description in cursor.description
    ]

    print(' | '.join(column_names))
    print('-' * 70)

    rows = cursor.fetchall()

    if not rows:
        print('Нет данных')
        return

    for row in rows:
        print(' | '.join(
            'NULL' if value is None else str(value)
            for value in row
        ))


def main():
    if not DATABASE_PATH.exists():
        print(f'База не найдена: {DATABASE_PATH}')
        return

    sql_text = SQL_PATH.read_text(encoding='utf-8')
    queries = read_queries(sql_text)

    with sqlite3.connect(DATABASE_PATH) as connection:
        for number, query in queries:
            try:
                print_result(connection, number, query)
            except sqlite3.Error as error:
                print(f'Ошибка в запросе {number}: {error}')


if __name__ == '__main__':
    main()