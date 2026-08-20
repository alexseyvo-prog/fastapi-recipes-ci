import sqlite3


DATABASE_NAME = 'database.db'


with open('create_schema.sql', 'r', encoding='utf-8') as sql_file:
    sql_script = sql_file.read()


with sqlite3.connect(DATABASE_NAME) as connection:
    connection.execute('PRAGMA foreign_keys = ON')
    connection.executescript(sql_script)
    connection.commit()


print(f'База данных {DATABASE_NAME} успешно создана')