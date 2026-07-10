# Импортируем необходимые модули
import os  # Для работы с путями к файлам
import re  # Для работы с регулярными выражениями
import random  # Для генерации случайных значений
from datetime import datetime, timedelta  # Для работы с временем
from flask import Flask  # Для создания веб-сервера

# Создаём объект Flask-приложения
app = Flask(__name__)


# --------------------
# Задача 1: /hello_world
# --------------------
# Создаём endpoint, который возвращает текст "Привет, мир!"
@app.route('/hello_world')
def get_hello():
   return "Привет, мир!"  # Возвращаем строку пользователю


# --------------------
# Задача 2: /cars
# --------------------
# Список машин создаём один раз в глобальной области видимости
cars = ['Chevrolet', 'Renault', 'Ford', 'Lada']


@app.route('/cars')
def get_cars():
   # Возвращаем список машин через запятую
   return ", ".join(cars)


# --------------------
# Задача 3: /cats
# --------------------
# Список пород кошек тоже в глобальной области видимости
cats = ['Корниш рекс', 'Русская голубая', 'Шотландская вислоухая', 'Мэйн-Кун', 'Манчкин']


@app.route('/cats')
def get_cats():
   # Возвращаем случайную породу кошки
   return random.choice(cats)


# --------------------
# Задача 4: /get_time/now
# --------------------
@app.route('/get_time/now')
def get_current_time():
   # Получаем текущее время
   current_time = datetime.now()
   # Возвращаем его в формате строки
   return f"Точное время: {current_time}"


# --------------------
# Задача 5: /get_time/future
# --------------------
@app.route('/get_time/future')
def get_future_time():
   # Получаем текущее время и добавляем 1 час
   current_time_after_hour = datetime.now() + timedelta(hours=1)
   return f"Точное время через час будет: {current_time_after_hour}"


# --------------------
# Задача 6: /get_random_word
# --------------------
# Глобальная переменная для хранения списка слов из книги
words = []


def get_words():
   """
   Функция возвращает список всех слов из книги 'war_and_peace.txt'.
   Файл открывается один раз при первом обращении.
   """
   if not words:  # Если список ещё не заполнен
       BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Абсолютный путь к папке проекта
       BOOK_FILE = os.path.join(BASE_DIR, 'war_and_peace.txt')  # Путь к файлу
       WORD_PATTERN = r'\b\w+\b'  # Регулярное выражение для поиска слов

       # Открываем файл и читаем слова
       with open(BOOK_FILE, encoding='utf-8') as book:
           book_words = re.findall(WORD_PATTERN, book.read())
           words.extend(book_words)  # Добавляем слова в глобальный список
   return words


@app.route('/get_random_word')
def get_random_word():
   # Возвращаем случайное слово из списка
   return random.choice(get_words())


# --------------------
# Задача 7: /counter
# --------------------
# Глобальная переменная-счётчик
counter = 0


@app.route('/counter')
def get_counter():
   global counter  # Используем глобальную переменную
   counter += 1  # Увеличиваем счётчик при каждом обращении
   return str(counter)  # Возвращаем число как строку


# --------------------
# Запуск сервера
# --------------------
if __name__ == '__main__':
   # Запускаем сервер на порту 8080 с включенным режимом отладки
   app.run(debug=True, port=8080)