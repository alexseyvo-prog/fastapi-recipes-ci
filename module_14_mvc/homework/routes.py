from flask import Flask, render_template, redirect, url_for, request
from typing import List, Optional

from models import (
    init_db,
    get_all_books,
    get_book_by_id,
    get_books_by_author,
    DATA,
    add_book,
)
from forms import AddBookForm

app: Flask = Flask(__name__)

app.config['SECRET_KEY'] = 'your-secret-key-here'


@app.route('/books')
def all_books() -> str:
    return render_template(
        'index.html',
        books=get_all_books(),
    )


@app.route('/books/<int:book_id>')
def book_detail(book_id: int) -> str:
    """
    Страница отдельной книги.

    При показе книги счётчик просмотров увеличивается на 1.
    """
    book = get_book_by_id(book_id)

    if book is None:
        return "Book not found", 404

    return render_template(
        'book_detail.html',
        book=book,
    )


@app.route('/books/form', methods=['GET', 'POST'])
def get_books_form() -> str:
    form = AddBookForm()

    if form.validate_on_submit():
        title = form.book_title.data
        author = form.author_name.data

        add_book(title=title, author=author)

        return redirect(url_for('all_books'))

    return render_template(
        'add_book.html',
        form=form,
    )


@app.route('/books/author')
def books_by_author() -> str:
    author = request.args.get('author', '')

    books = get_books_by_author(author) if author else []

    return render_template(
        'books_by_author.html',
        author=author,
        books=books,
    )


if __name__ == '__main__':
    init_db(DATA)
    app.run(debug=True)