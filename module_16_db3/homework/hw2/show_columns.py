import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).parent / 'hw.db'


def main():
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)

        tables = cursor.fetchall()

        for (table_name,) in tables:
            print(f'\nТаблица: {table_name}')
            print('-' * 50)

            cursor.execute(f'PRAGMA table_info("{table_name}")')
            columns = cursor.fetchall()

            for column in columns:
                column_id = column[0]
                column_name = column[1]
                column_type = column[2]
                not_null = column[3]
                default_value = column[4]
                primary_key = column[5]

                print(
                    f'{column_id}: '
                    f'{column_name} '
                    f'({column_type}), '
                    f'NOT NULL={bool(not_null)}, '
                    f'PK={bool(primary_key)}, '
                    f'DEFAULT={default_value}'
                )


if __name__ == '__main__':
    main()