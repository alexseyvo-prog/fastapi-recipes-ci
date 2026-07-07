from flask import Flask
from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import DataRequired
from hw2_validators import number_length, NumberLength

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev"
app.config["WTF_CSRF_ENABLED"] = False


class PhoneFormFunc(FlaskForm):
    phone = IntegerField(
        validators=[
            DataRequired(),
            number_length(10, 10, message="Phone must be 10 digits long"),
        ]
    )


class PhoneFormClass(FlaskForm):
    phone = IntegerField(
        validators=[
            DataRequired(),
            NumberLength(10, 10, message="Phone must be 10 digits long"),
        ]
    )


def test_func_valid_10_digits():
    """Функциональный валидатор: корректный телефон из 10 цифр проходит валидацию."""
    with app.test_request_context(method="POST", data={"phone": "1234567890"}):
        form = PhoneFormFunc()
        assert form.validate() is True
        assert form.errors == {}


def test_func_invalid_5_digits():
    """Функциональный валидатор: телефон из 5 цифр НЕ проходит валидацию."""
    with app.test_request_context(method="POST", data={"phone": "12345"}):
        form = PhoneFormFunc()
        assert form.validate() is False
        assert "phone" in form.errors


def test_class_valid_10_digits():
    """Классовый валидатор: корректный телефон из 10 цифр проходит валидацию."""
    with app.test_request_context(method="POST", data={"phone": "1234567890"}):
        form = PhoneFormClass()
        assert form.validate() is True
        assert form.errors == {}


def test_class_invalid_5_digits():
    """Классовый валидатор: телефон из 5 цифр НЕ проходит валидацию."""
    with app.test_request_context(method="POST", data={"phone": "12345"}):
        form = PhoneFormClass()
        assert form.validate() is False
        assert "phone" in form.errors