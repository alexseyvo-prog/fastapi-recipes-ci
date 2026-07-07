
"""
В эндпоинт /registration добавьте все валидаторы:

1) email (текст, обязательно для заполнения, валидация формата);
2) phone (число, обязательно для заполнения, длина — десять символов, только положительные числа);
3) name (текст, обязательно для заполнения);
4) address (текст, обязательно для заполнения);
5) index (только числа, обязательно для заполнения);
6) comment (текст, необязательно для заполнения).
"""

from flask import Flask
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField
from wtforms.validators import DataRequired, Email, NumberRange, Length


app = Flask(__name__)


class RegistrationForm(FlaskForm):
    """
    Форма регистрации с проверками:

    - email: обязательный текст, формат email;
    - phone: обязательное число, положительное, ровно 10 цифр;
    - name: обязательный текст;
    - address: обязательный текст;
    - index: обязательное число;
    - comment: текст, опционально.
    """

    # email: текст, обязателен, формат email
    email = StringField(
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Invalid email format"),
        ]
    )

    # phone: здесь удобнее хранить как строку,
    # чтобы валидировать длину (10 символов) и число через кастомную логику
    phone = StringField(
        validators=[
            DataRequired(message="Phone is required"),
            Length(min=10, max=10, message="Phone must be 10 digits long"),
        ]
    )

    # name: текст, обязателен
    name = StringField(
        validators=[
            DataRequired(message="Name is required"),
        ]
    )

    # address: текст, обязателен
    address = StringField(
        validators=[
            DataRequired(message="Address is required"),
        ]
    )

    # index: только числа, обязателен
    index = IntegerField(
        validators=[
            DataRequired(message="Index is required"),
        ]
    )

    # comment — необязательное текстовое поле (без DataRequired)
    comment = StringField()


@app.route("/registration", methods=["POST"])
def registration():
    """
    Эндпоинт /registration:

    - принимает POST с полями формы;
    - валидирует все поля согласно заданным валидаторам;
    - при успехе возвращает сообщение об успешной регистрации;
    - при ошибке — список ошибок и код 400.
    """
    form = RegistrationForm()

    # Дополнительная проверка: phone — только положительные числа.
    # WTForms уже проверил длину, здесь проверим, что все символы — цифры.
    if form.validate_on_submit():
        email = form.email.data
        phone_raw = form.phone.data

        if not phone_raw.isdigit():
            # добавляем ошибку к полю phone
            form.phone.errors.append("Phone must contain only digits")
            return f"Invalid input, {form.errors}", 400

        phone_int = int(phone_raw)
        if phone_int <= 0:
            form.phone.errors.append("Phone must be a positive number")
            return f"Invalid input, {form.errors}", 400

        # если все проверки прошли
        return f"Successfully registered user {email} with phone +7{phone_raw}"

    # form.errors: словарь {имя_поля: [сообщения об ошибках]}
    return f"Invalid input, {form.errors}", 400


if __name__ == "__main__":
    # Отключаем CSRF для упрощения локального тестирования (в обучающем задании).
    app.config["SECRET_KEY"] = "dev-secret-key"
    app.config["WTF_CSRF_ENABLED"] = False
    app.run(debug=True)


