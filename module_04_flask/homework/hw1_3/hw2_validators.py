"""
Довольно неудобно использовать встроенный валидатор NumberRange для ограничения числа по его длине.
Создадим свой для поля phone. Создайте валидатор обоими способами.
Валидатор должен принимать на вход параметры min и max — минимальная и максимальная длина,
а также опциональный параметр message (см. рекомендации к предыдущему заданию).
"""
from typing import Optional

from flask_wtf import FlaskForm
from wtforms import Field
from wtforms.validators import ValidationError


def number_length(min: int, max: int, message: Optional[str] = None):
    """
    Функциональный валидатор длины числа.

    Использование:
        phone = IntegerField(validators=[InputRequired(), number_length(10, 10)])

    Параметры:
    - min: минимальное количество цифр.
    - max: максимальное количество цифр.
    - message: сообщение об ошибке (опционально). Если не задано,
      формируется стандартное сообщение вида:
      "Number length must be between {min} and {max} digits".

    Внутренняя логика:
    - Берём значение field.data.
    - Если оно None или пустое, считаем длину 0.
    - Приводим значение к строке и считаем количество цифр (символов 0–9).
    - Если число цифр < min или > max, бросаем ValidationError.
    """

    if message is None:
        message = f"Number length must be between {min} and {max} digits"

    def _number_length(form: FlaskForm, field: Field):
        # Значение поля
        data = field.data

        # Обрабатываем None и пустые значения
        if data is None:
            length = 0
        else:
            # Приводим к строке и вытаскиваем только цифры
            digits = [ch for ch in str(data) if ch.isdigit()]
            length = len(digits)

        # Проверяем диапазон длины
        if length < min or length > max:
            raise ValidationError(message)

    return _number_length


class NumberLength:
    """
    Классовый валидатор длины числа.

    Использование:
        phone = IntegerField(validators=[InputRequired(), NumberLength(min=10, max=10)])

    Параметры конструктора:
    - min: минимальное количество цифр.
    - max: максимальное количество цифр.
    - message: сообщение об ошибке (опционально). Если не задано,
      формируется стандартное сообщение вида:
      "Number length must be between {min} and {max} digits".

    Логика __call__ аналогична функциональной версии number_length:
    - считает количество цифр в значении поля;
    - если длина вне диапазона [min, max], бросает ValidationError.
    """

    def __init__(self, min: int, max: int, message: Optional[str] = None):
        self.min = min
        self.max = max
        if message is None:
            message = f"Number length must be between {min} and {max} digits"
        self.message = message

    def __call__(self, form: FlaskForm, field: Field):
        data = field.data

        if data is None:
            length = 0
        else:
            digits = [ch for ch in str(data) if ch.isdigit()]
            length = len(digits)

        if length < self.min or length > self.max:
            raise ValidationError(self.message)
