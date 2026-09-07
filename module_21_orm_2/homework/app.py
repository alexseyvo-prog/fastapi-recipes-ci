from flask import Flask, request, Response
from sqlalchemy import create_engine, func, event, and_
from sqlalchemy.orm import sessionmaker, joinedload, selectinload, subqueryload
from datetime import datetime, timedelta
import json
import csv
import io

from models import Base, Author, Book, Student, ReceivingBook, set_sqlite_pragma

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
engine = create_engine(f'sqlite:///{db_path}', echo=False)

# Включение поддержки внешних ключей в SQLite
event.listen(engine, "connect", set_sqlite_pragma)

Session = sessionmaker(bind=engine)


# ============================================================
# РОУТ ДЛЯ ИМПОРТА СТУДЕНТОВ ИЗ CSV
# ============================================================


@app.route('/api/students/import', methods=['POST'])
def import_students():
    """
    Импорт студентов из CSV-файла.
    Формат CSV (разделитель ;):
    name;surname;phone;email;average_score;scholarship
    Иван;Иванов;+79001112233;ivanov@test.com;4.5;true

    Использует Session.bulk_insert_mappings() для массовой вставки.
    """
    session = Session()
    try:
        # Проверяем наличие файла
        if 'file' not in request.files:
            return json_response({'error': 'Файл не найден. Используйте ключ "file"'}, 400)

        file = request.files['file']

        if file.filename == '':
            return json_response({'error': 'Файл не выбран'}, 400)

        # Читаем содержимое файла
        file_content = file.read().decode('utf-8')
        file_io = io.StringIO(file_content)

        # Используем csv.DictReader с разделителем ";"
        reader = csv.DictReader(file_io, delimiter=';')

        # Проверяем наличие обязательных полей
        required_fields = {'name', 'surname', 'phone', 'email', 'average_score', 'scholarship'}
        if not required_fields.issubset(set(reader.fieldnames or [])):
            return json_response({
                'error': f'Отсутствуют обязательные поля. Ожидаются: {required_fields}',
                'found_fields': reader.fieldnames
            }, 400)

        # Подготавливаем данные для массовой вставки
        students_data = []
        errors = []

        for idx, row in enumerate(reader, start=2):  # start=2, т.к. первая строка - заголовок
            try:
                # Преобразуем scholarship из строки в boolean
                scholarship_value = row['scholarship'].strip().lower()
                if scholarship_value in ('true', '1', 'yes', 'да'):
                    scholarship = True
                elif scholarship_value in ('false', '0', 'no', 'нет'):
                    scholarship = False
                else:
                    errors.append(f"Строка {idx}: неверное значение scholarship '{row['scholarship']}'")
                    continue

                # Преобразуем average_score в float
                try:
                    average_score = float(row['average_score'])
                except ValueError:
                    errors.append(f"Строка {idx}: неверное значение average_score '{row['average_score']}'")
                    continue

                # Добавляем данные в список
                students_data.append({
                    'name': row['name'].strip(),
                    'surname': row['surname'].strip(),
                    'phone': row['phone'].strip(),
                    'email': row['email'].strip(),
                    'average_score': average_score,
                    'scholarship': scholarship,
                })

            except Exception as e:
                errors.append(f"Строка {idx}: ошибка обработки - {str(e)}")

        # Массовая вставка через bulk_insert_mappings
        if students_data:
            session.bulk_insert_mappings(Student, students_data)
            session.commit()

        result = {
            'message': f'Успешно импортировано {len(students_data)} студентов',
            'imported_count': len(students_data),
        }

        if errors:
            result['errors'] = errors
            result['status'] = 'partial_success'
        else:
            result['status'] = 'success'

        return json_response(result, 201 if students_data else 400)

    except Exception as e:
        session.rollback()
        return json_response({'error': f'Ошибка импорта: {str(e)}'}, 500)
    finally:
        session.close()


# ============================================================
# СТАРЫЕ РОУТЫ (без изменений)
# ============================================================


@app.route('/api/books', methods=['GET'])
def get_all_books():
    """Получение всех книг в библиотеке (жадная подгрузка автора через joinedload)."""
    session = Session()
    try:
        books = session.query(Book).options(joinedload(Book.author)).all()
        return json_response([
            {
                'id': book.id,
                'name': book.name,
                'count': book.count,
                'release_date': book.release_date.isoformat() if book.release_date else None,
                'author_id': book.author_id,
                'author': f'{book.author.surname} {book.author.name}' if book.author else None,
            }
            for book in books
        ])
    finally:
        session.close()


@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Получение книги по ID (жадная подгрузка автора)."""
    session = Session()
    try:
        book = session.query(Book).options(joinedload(Book.author)).filter_by(id=book_id).first()
        if not book:
            return json_response({'error': f'Книга с id {book_id} не найдена'}, 404)

        return json_response({
            'id': book.id,
            'name': book.name,
            'count': book.count,
            'release_date': book.release_date.isoformat() if book.release_date else None,
            'author_id': book.author_id,
            'author': f'{book.author.surname} {book.author.name}' if book.author else None,
        })
    finally:
        session.close()


@app.route('/api/authors', methods=['GET'])
def get_all_authors():
    """Получение всех авторов (жадная подгрузка книг через selectinload)."""
    session = Session()
    try:
        authors = session.query(Author).options(selectinload(Author.books)).all()
        return json_response([
            {
                'id': author.id,
                'name': author.name,
                'surname': author.surname,
                'books_count': len(author.books),
            }
            for author in authors
        ])
    finally:
        session.close()


@app.route('/api/students', methods=['GET'])
def get_all_students():
    """Получение всех студентов (жадная подгрузка выдач через subqueryload)."""
    session = Session()
    try:
        students = session.query(Student).options(subqueryload(Student.receivings)).all()
        return json_response([
            {
                'id': student.id,
                'name': student.name,
                'surname': student.surname,
                'phone': student.phone,
                'email': student.email,
                'average_score': student.average_score,
                'scholarship': student.scholarship,
                'books_count': len(student.receivings),
            }
            for student in students
        ])
    finally:
        session.close()


@app.route('/api/debtors', methods=['GET'])
def get_debtors():
    """Получение списка должников (книга > 14 дней)."""
    session = Session()
    try:
        now = datetime.now()
        threshold = now - timedelta(days=14)

        debtors = session.query(ReceivingBook).options(
            joinedload(ReceivingBook.book),
            joinedload(ReceivingBook.student)
        ).filter(
            ReceivingBook.date_of_return.is_(None),
            ReceivingBook.date_of_issue < threshold,
        ).all()

        result = []
        for record in debtors:
            days_held = (now - record.date_of_issue).days

            result.append({
                'student_id': record.student.id,
                'student_name': f'{record.student.surname} {record.student.name}',
                'book_id': record.book.id,
                'book_name': record.book.name,
                'days_held': days_held,
                'date_of_issue': record.date_of_issue.isoformat(),
            })

        return json_response(result)
    finally:
        session.close()


@app.route('/api/give', methods=['POST'])
def give_book():
    """Выдать книгу студенту."""
    session = Session()
    try:
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
    except Exception as e:
        session.rollback()
        return json_response({'error': str(e)}, 500)
    finally:
        session.close()


@app.route('/api/return', methods=['POST'])
def return_book():
    """Сдать книгу в библиотеку."""
    session = Session()
    try:
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
        days_held = (receiving.date_of_return - receiving.date_of_issue).days

        # Увеличиваем количество доступных экземпляров
        book = session.query(Book).filter_by(id=book_id).first()
        book.count += 1

        # Получаем студента для сообщения
        student = session.query(Student).filter_by(id=student_id).first()

        session.commit()

        return json_response({
            'message': f'Книга "{book.name}" возвращена студентом {student.surname} {student.name}',
            'days_held': days_held,
        })
    except Exception as e:
        session.rollback()
        return json_response({'error': str(e)}, 500)
    finally:
        session.close()


@app.route('/api/search', methods=['GET'])
def search_books():
    """Поиск книги по названию."""
    session = Session()
    try:
        query = request.args.get('q', '')

        if not query:
            return json_response({'error': 'Параметр q обязателен'}, 400)

        books = session.query(Book).options(joinedload(Book.author)).filter(
            Book.name.ilike(f'%{query}%')
        ).all()

        return json_response([
            {
                'id': book.id,
                'name': book.name,
                'count': book.count,
                'release_date': book.release_date.isoformat() if book.release_date else None,
                'author_id': book.author_id,
                'author': f'{book.author.surname} {book.author.name}' if book.author else None,
            }
            for book in books
        ])
    finally:
        session.close()


@app.route('/api/students/<int:student_id>/books', methods=['GET'])
def get_student_books(student_id):
    """Получить все книги, выданные студенту (включая сданные)."""
    session = Session()
    try:
        student = session.query(Student).options(
            subqueryload(Student.receivings).joinedload(ReceivingBook.book)
        ).filter_by(id=student_id).first()
        if not student:
            return json_response({'error': f'Студент с id {student_id} не найден'}, 404)

        result = []
        for rec in student.receivings:
            result.append({
                'receiving_id': rec.id,
                'book_id': rec.book.id,
                'book_name': rec.book.name,
                'date_of_issue': rec.date_of_issue.isoformat(),
                'date_of_return': rec.date_of_return.isoformat() if rec.date_of_return else None,
                'is_returned': rec.date_of_return is not None,
            })

        return json_response(result)
    finally:
        session.close()


@app.route('/api/students/<int:student_id>/active-books', methods=['GET'])
def get_student_active_books(student_id):
    """Получить книги, которые сейчас у студента (не сданы)."""
    session = Session()
    try:
        student = session.query(Student).options(
            subqueryload(Student.receivings).joinedload(ReceivingBook.book)
        ).filter_by(id=student_id).first()
        if not student:
            return json_response({'error': f'Студент с id {student_id} не найден'}, 404)

        result = []
        for rec in student.receivings:
            if rec.date_of_return is None:
                days_held = (datetime.now() - rec.date_of_issue).days
                result.append({
                    'receiving_id': rec.id,
                    'book_id': rec.book.id,
                    'book_name': rec.book.name,
                    'date_of_issue': rec.date_of_issue.isoformat(),
                    'days_held': days_held,
                    'is_overdue': days_held > 14,
                })

        return json_response(result)
    finally:
        session.close()


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Получить статистику библиотеки."""
    session = Session()
    try:
        total_books = session.query(func.sum(Book.count)).scalar() or 0
        total_titles = session.query(func.count(Book.id)).scalar() or 0
        total_students = session.query(func.count(Student.id)).scalar() or 0
        active_receivings = session.query(func.count(ReceivingBook.id)).filter(
            ReceivingBook.date_of_return.is_(None)
        ).scalar() or 0

        return json_response({
            'total_books': total_books,
            'total_titles': total_titles,
            'total_students': total_students,
            'active_receivings': active_receivings,
        })
    finally:
        session.close()


@app.route('/api/authors/<int:author_id>/books-count', methods=['GET'])
def get_author_books_count(author_id):
    """Получить кол-во оставшихся в библиотеке книг по автору."""
    session = Session()
    try:
        author = session.query(Author).filter_by(id=author_id).first()
        if not author:
            return json_response({'error': f'Автор с id {author_id} не найден'}, 404)

        # Суммируем count всех книг автора
        total_count = session.query(func.sum(Book.count)).filter(
            Book.author_id == author_id
        ).scalar() or 0

        return json_response({
            'author_id': author_id,
            'author': f'{author.surname} {author.name}',
            'total_books_count': total_count,
        })
    finally:
        session.close()


@app.route('/api/students/<int:student_id>/unread-books-by-same-author', methods=['GET'])
def get_unread_books_by_same_author(student_id):
    """
    Получить список книг, которые студент не читал,
    при этом другие книги этого автора студент уже брал.
    """
    session = Session()
    try:
        student = session.query(Student).filter_by(id=student_id).first()
        if not student:
            return json_response({'error': f'Студент с id {student_id} не найден'}, 404)

        # Получаем все книги, которые брал студент
        taken_book_ids = session.query(ReceivingBook.book_id).filter(
            ReceivingBook.student_id == student_id
        ).distinct()

        # Получаем авторов книг, которые студент уже брал
        taken_authors = session.query(Book.author_id).join(ReceivingBook).filter(
            ReceivingBook.student_id == student_id
        ).distinct()

        # Получаем все книги этих авторов
        books_by_taken_authors = session.query(Book).filter(
            Book.author_id.in_(taken_authors)
        ).all()

        # Фильтруем книги, которые студент ещё не брал
        unread_books = [
            book for book in books_by_taken_authors
            if book.id not in taken_book_ids
        ]

        result = [
            {
                'id': book.id,
                'name': book.name,
                'author_id': book.author_id,
                'author': f'{book.author.surname} {book.author.name}',
                'count': book.count,
                'release_date': book.release_date.isoformat() if book.release_date else None,
            }
            for book in unread_books
        ]

        return json_response(result)
    finally:
        session.close()


@app.route('/api/statistics/books-per-month', methods=['GET'])
def get_books_per_month():
    """Получить среднее кол-во книг, которые студенты брали в этом месяце."""
    session = Session()
    try:
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Считаем количество выдач в этом месяце
        count = session.query(func.count(ReceivingBook.id)).filter(
            ReceivingBook.date_of_issue >= month_start
        ).scalar() or 0

        # Считаем количество студентов, которые брали книги в этом месяце
        students_count = session.query(func.count(func.distinct(ReceivingBook.student_id))).filter(
            ReceivingBook.date_of_issue >= month_start
        ).scalar() or 0

        # Среднее кол-во книг на студента
        average = count / students_count if students_count > 0 else 0

        return json_response({
            'month': month_start.strftime('%Y-%m'),
            'total_books_taken': count,
            'students_count': students_count,
            'average_books_per_student': round(average, 2),
        })
    finally:
        session.close()


@app.route('/api/statistics/most-popular-book-high-score', methods=['GET'])
def get_most_popular_book_high_score():
    """Получить самую популярную книгу среди студентов со средним баллом > 4.0."""
    session = Session()
    try:
        # Получаем самую популярную книгу среди студентов с average_score > 4.0
        result = session.query(
            Book.id,
            Book.name,
            func.count(ReceivingBook.id).label('times_taken')
        ).join(ReceivingBook).join(Student).filter(
            Student.average_score > 4.0
        ).group_by(Book.id, Book.name).order_by(
            func.count(ReceivingBook.id).desc()
        ).first()

        if not result:
            return json_response({
                'message': 'Нет данных о выдачах студентам с баллом > 4.0',
                'book': None,
            })

        book_id, book_name, times_taken = result

        return json_response({
            'book_id': book_id,
            'book_name': book_name,
            'times_taken': times_taken,
        })
    finally:
        session.close()


@app.route('/api/statistics/top-10-students-year', methods=['GET'])
def get_top_10_students_year():
    """Получить ТОП-10 самых читающих студентов в этом году."""
    session = Session()
    try:
        now = datetime.now()
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

        # ТОП-10 студентов по количеству выданных книг в этом году
        results = session.query(
            Student.id,
            Student.name,
            Student.surname,
            func.count(ReceivingBook.id).label('books_count')
        ).join(ReceivingBook).filter(
            ReceivingBook.date_of_issue >= year_start
        ).group_by(Student.id, Student.name, Student.surname).order_by(
            func.count(ReceivingBook.id).desc()
        ).limit(10).all()

        top_students = [
            {
                'rank': idx + 1,
                'student_id': student_id,
                'name': name,
                'surname': surname,
                'books_count': books_count,
            }
            for idx, (student_id, name, surname, books_count) in enumerate(results)
        ]

        return json_response({
            'year': year_start.year,
            'top_students': top_students,
        })
    finally:
        session.close()


if __name__ == '__main__':
    app.run(debug=True)