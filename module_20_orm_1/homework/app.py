# app.py
from flask import Flask, request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json

from models import Base, Author, Book, Student, ReceivingBook

app = Flask(__name__)


def json_response(data, status=200):
    """Вспомогательная функция для JSON-ответа с Unicode."""
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        status=status,
        mimetype='application/json'
    )


# Подключение к БД
db_path = 'library.db'
engine = create_engine(f'sqlite:///{db_path}')
Session = sessionmaker(bind=engine)
session = Session()


@app.route('/api/books', methods=['GET'])
def get_all_books():
    """Получение всех книг в библиотеке."""
    books = session.query(Book).all()
    return json_response([
        {
            'id': book.id,
            'name': book.name,
            'count': book.count,
            'release_date': book.release_date.isoformat() if book.release_date else None,
            'author_id': book.author_id,
        }
        for book in books
    ])


@app.route('/api/debtors', methods=['GET'])
def get_debtors():
    """Получение списка должников (книга > 14 дней)."""
    debtors = session.query(ReceivingBook).filter(
        ReceivingBook.date_of_return.is_(None),
    ).all()

    result = []
    for record in debtors:
        if record.count_date_with_book > 14:
            student = session.query(Student).filter_by(id=record.student_id).first()
            book = session.query(Book).filter_by(id=record.book_id).first()
            result.append({
                'student_id': student.id,
                'student_name': f'{student.surname} {student.name}',
                'book_id': book.id,
                'book_name': book.name,
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

    student = session.query(Student).filter_by(id=student_id).first()
    if not student:
        return json_response({'error': f'Студент с id {student_id} не найден'}, 404)

    book = session.query(Book).filter_by(id=book_id).first()
    if not book:
        return json_response({'error': f'Книга с id {book_id} не найдена'}, 404)

    # Проверка количества экземпляров
    if book.count <= 0:
        return json_response({'error': 'Все экземпляры книги уже выданы'}, 409)

    receiving = ReceivingBook(
        student_id=student_id,
        book_id=book_id,
        date_of_issue=datetime.now(),
        date_of_return=None,
    )

    # Уменьшаем количество доступных экземпляров
    book.count -= 1

    session.add(receiving)
    session.commit()

    return json_response({
        'message': f'Книга "{book.name}" выдана студенту {student.surname} {student.name}',
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
        ReceivingBook.date_of_return.is_(None),
    ).first()

    if not receiving:
        return json_response({
            'error': 'Такая связка студент-книга не найдена или книга уже сдана'
        }, 404)

    receiving.date_of_return = datetime.now()

    # Увеличиваем количество доступных экземпляров
    book = session.query(Book).filter_by(id=book_id).first()
    book.count += 1

    # Получаем студента для сообщения
    student = session.query(Student).filter_by(id=student_id).first()

    session.commit()

    return json_response({
        'message': f'Книга "{book.name}" возвращена студентом {student.surname} {student.name}',
        'days_held': receiving.count_date_with_book,
    })


@app.route('/api/search', methods=['GET'])
def search_books():
    """Поиск книги по названию."""
    query = request.args.get('q', '')

    if not query:
        return json_response({'error': 'Параметр q обязателен'}, 400)

    books = session.query(Book).filter(
        Book.name.ilike(f'%{query}%')
    ).all()

    return json_response([
        {
            'id': book.id,
            'name': book.name,
            'count': book.count,
            'release_date': book.release_date.isoformat() if book.release_date else None,
            'author_id': book.author_id,
        }
        for book in books
    ])


@app.route('/api/students/dormitory', methods=['GET'])
def get_students_with_dormitory():
    """Получить список студентов, у которых есть общежитие."""
    students = Student.with_dormitory(session)

    return json_response([
        {
            'id': s.id,
            'name': s.name,
            'surname': s.surname,
            'phone': s.phone,
            'email': s.email,
            'average_score': s.average_score,
            'scholarship': s.scholarship,
            'dormitory': s.dormitory,
        }
        for s in students
    ])


@app.route('/api/students/high-score', methods=['GET'])
def get_high_score_students():
    """Получить студентов со средним баллом выше указанного."""
    score_threshold = request.args.get('score', type=float)

    if score_threshold is None:
        return json_response({'error': 'Параметр score обязателен'}, 400)

    students = Student.with_average_score_above(session, score_threshold)

    return json_response([
        {
            'id': s.id,
            'name': s.name,
            'surname': s.surname,
            'phone': s.phone,
            'email': s.email,
            'average_score': s.average_score,
            'scholarship': s.scholarship,
        }
        for s in students
    ])


if __name__ == '__main__':
    app.run(debug=True)