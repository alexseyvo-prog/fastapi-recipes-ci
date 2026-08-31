# app.py
from flask import Flask, request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date
import json

from models import Base, Student, Book, ReceivingBook

app = Flask(__name__)


def json_response(data, status=200):
    """Вспомогательная функция для JSON-ответа с Unicode."""
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        status=status,
        mimetype='application/json'
    )


# Подключение к БД
engine = create_engine('sqlite:///library.db')
Session = sessionmaker(bind=engine)
session = Session()


@app.route('/api/books', methods=['GET'])
def get_all_books():
    """Получение всех книг в библиотеке."""
    books = session.query(Book).all()
    return json_response([
        {
            'book_id': book.book_id,
            'title': book.title,
            'author': book.author,
            'year': book.year,
        }
        for book in books
    ])


@app.route('/api/books', methods=['POST'])
def add_book():
    """Добавить новую книгу."""
    data = request.get_json()

    if not data or 'title' not in data or 'author' not in data:
        return json_response({'error': 'title и author обязательны'}, 400)

    book = Book(
        title=data['title'],
        author=data['author'],
        year=data.get('year'),
    )

    session.add(book)
    session.commit()

    return json_response({
        'book_id': book.book_id,
        'title': book.title,
        'author': book.author,
        'year': book.year,
    }, 201)


@app.route('/api/debtors', methods=['GET'])
def get_debtors():
    """Получение списка должников (книга > 14 дней)."""
    debtors = session.query(ReceivingBook).filter(
        ReceivingBook.date_return.is_(None),
    ).all()

    result = []
    for record in debtors:
        if record.count_date_with_book > 14:
            student = session.query(Student).filter_by(student_id=record.student_id).first()
            book = session.query(Book).filter_by(book_id=record.book_id).first()
            result.append({
                'student_id': student.student_id,
                'student_name': student.name,
                'book_id': book.book_id,
                'book_title': book.title,
                'days_held': record.count_date_with_book,
            })

    return json_response(result)


@app.route('/api/give', methods=['POST'])
def give_book():
    """Выдать книгу студенту."""
    data = request.get_json()

    if not data or 'student_id' not in data or 'book_id' not in data:
        return json_response({'error': 'student_id и book_id обязательны'}, 400)

    student_id = data['student_id']
    book_id = data['book_id']

    student = session.query(Student).filter_by(student_id=student_id).first()
    if not student:
        return json_response({'error': f'Студент с id {student_id} не найден'}, 404)

    book = session.query(Book).filter_by(book_id=book_id).first()
    if not book:
        return json_response({'error': f'Книга с id {book_id} не найдена'}, 404)

    receiving = ReceivingBook(
        student_id=student_id,
        book_id=book_id,
        date_get=date.today(),
        date_return=None,
    )

    session.add(receiving)
    session.commit()

    return json_response({
        'message': f'Книга "{book.title}" выдана студенту {student.name}',
        'id': receiving.id,
    }, 201)


@app.route('/api/return', methods=['POST'])
def return_book():
    """Сдать книгу в библиотеку."""
    data = request.get_json()

    if not data or 'student_id' not in data or 'book_id' not in data:
        return json_response({'error': 'student_id и book_id обязательны'}, 400)

    student_id = data['student_id']
    book_id = data['book_id']

    receiving = session.query(ReceivingBook).filter(
        ReceivingBook.student_id == student_id,
        ReceivingBook.book_id == book_id,
        ReceivingBook.date_return.is_(None),
    ).first()

    if not receiving:
        return json_response({
            'error': 'Такая связка студент-книга не найдена или книга уже сдана'
        }, 404)

    receiving.date_return = date.today()
    session.commit()

    book = session.query(Book).filter_by(book_id=book_id).first()
    student = session.query(Student).filter_by(student_id=student_id).first()

    return json_response({
        'message': f'Книга "{book.title}" возвращена студентом {student.name}',
        'days_held': receiving.count_date_with_book,
    })


@app.route('/api/search', methods=['GET'])
def search_books():
    """Поиск книги по названию."""
    query = request.args.get('q', '')

    if not query:
        return json_response({'error': 'Параметр q обязателен'}, 400)

    books = session.query(Book).filter(
        Book.title.ilike(f'%{query}%')
    ).all()

    return json_response([
        {
            'book_id': book.book_id,
            'title': book.title,
            'author': book.author,
            'year': book.year,
        }
        for book in books
    ])


@app.route('/api/students/dormitory', methods=['GET'])
def get_students_with_dormitory():
    """Получить список студентов, у которых есть общежитие."""
    students = Student.with_dormitory(session)

    return json_response([
        {
            'student_id': s.student_id,
            'name': s.name,
            'dormitory': s.dormitory,
            'gpa': s.gpa,
        }
        for s in students
    ])


@app.route('/api/students/high-gpa', methods=['GET'])
def get_high_gpa_students():
    """Получить студентов со средним баллом выше указанного."""
    gpa_threshold = request.args.get('gpa', type=float)

    if gpa_threshold is None:
        return json_response({'error': 'Параметр gpa обязателен'}, 400)

    students = Student.with_gpa_above(session, gpa_threshold)

    return json_response([
        {
            'student_id': s.student_id,
            'name': s.name,
            'dormitory': s.dormitory,
            'gpa': s.gpa,
        }
        for s in students
    ])


if __name__ == '__main__':
    app.run(debug=True)