from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddBookForm(FlaskForm):
    """
    Форма добавления книги.

    Оба поля обязательны для заполнения.
    """

    book_title = StringField(
        'Book title',
        validators=[DataRequired(message='Book title is required.')],
    )

    author_name = StringField(
        'Author full name',
        validators=[DataRequired(message='Author full name is required.')],
    )

    submit = SubmitField('Add new book')