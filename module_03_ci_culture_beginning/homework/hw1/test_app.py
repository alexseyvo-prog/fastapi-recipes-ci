from freezegun import freeze_time
from hello_word_with_day import app, get_weekday_greeting


# ===== Тесты для get_weekday_greeting =====
# Этот блок тестов проверяет, что функция get_weekday_greeting
# возвращает правильное пожелание для каждого дня недели.

def test_debug_get_weekday_greeting_direct():
    # Отладочный тест: просто вызываем get_weekday_greeting без заморозки времени
    # и убеждаемся, что функция возвращает какую‑то строку, а не None.
    result = get_weekday_greeting()
    print("DEBUG get_weekday_greeting:", repr(result))
    assert result is not None


def test_get_weekday_greeting_monday():
    # Замораживаем время на понедельник 2024-03-11
    # и проверяем, что функция вернёт пожелание именно для понедельника.
    with freeze_time("2026-06-01"):  # понедельник
        assert get_weekday_greeting() == "Хорошего понедельника"


def test_get_weekday_greeting_tuesday():
    # Замораживаем время на вторник и проверяем, что вернулся текст для вторника.
    with freeze_time("2026-06-02"):  # вторник
        assert get_weekday_greeting() == "Хорошего вторника"


def test_get_weekday_greeting_wednesday():
    # Замораживаем время на среду и ожидаем «Хорошей среды».
    with freeze_time("2026-06-03"):  # среда
        assert get_weekday_greeting() == "Хорошей среды"


def test_get_weekday_greeting_thursday():
    # Замораживаем время на четверг и ожидаем «Хорошего четверга».
    with freeze_time("2026-06-04"):  # четверг
        assert get_weekday_greeting() == "Хорошего четверга"


def test_get_weekday_greeting_friday():
    # Замораживаем время на пятницу и ожидаем «Хорошей пятницы».
    with freeze_time("2026-06-05"):  # пятница
        assert get_weekday_greeting() == "Хорошей пятницы"


def test_get_weekday_greeting_saturday():
    # Замораживаем время на субботу и ожидаем «Хорошей субботы».
    with freeze_time("2026-06-06"):  # суббота
        assert get_weekday_greeting() == "Хорошей субботы"


def test_get_weekday_greeting_sunday():
    # Замораживаем время на воскресенье и ожидаем «Хорошего воскресенья».
    with freeze_time("2026-06-07"):  # воскресенье
        assert get_weekday_greeting() == "Хорошего воскресенья"


# ===== Тесты для Flask-роута /hello-world/<name> =====
# Этот блок тестов проверяет HTTP-эндпоинт /hello-world/<name>,
# который возвращает строку с приветствием и пожеланием хорошего дня.

def test_hello_world_monday():
    # Включаем тестовый режим у Flask-приложения
    # и создаём тестовый клиент для отправки HTTP-запросов.
    app.config["TESTING"] = True
    client = app.test_client()

    name = "Иван"

    # Замораживаем время на понедельник и делаем GET-запрос к /hello-world/Иван.
    with freeze_time("2026-06-01"):  # понедельник
        response = client.get(f"/hello-world/{name}")
        # Проверяем, что сервер успешно ответил (код 200).
        assert response.status_code == 200

        # Декодируем тело ответа из байтов в строку.
        text = response.data.decode("utf-8")
        # Ожидаем строгое совпадение текста с приветствием для понедельника.
        assert text == "Привет, Иван. Хорошего понедельника!"


def test_hello_world_wednesday():
    # Настраиваем тестовый режим и тестовый клиент так же, как в предыдущем тесте.
    app.config["TESTING"] = True
    client = app.test_client()

    name = "Мария"

    # Замораживаем время на среду и делаем запрос к /hello-world/Мария.
    with freeze_time("2026-06-03"):  # среда
        response = client.get(f"/hello-world/{name}")
        assert response.status_code == 200

        text = response.data.decode("utf-8")
        # Проверяем, что в ответе корректное приветствие для среды.
        assert text == "Привет, Мария. Хорошей среды!"


def test_hello_world_sunday():
    # Включаем тестовый режим и создаём тестовый клиент.
    app.config["TESTING"] = True
    client = app.test_client()

    name = "Гость"

    # Замораживаем время на воскресенье и делаем запрос к /hello-world/Гость.
    with freeze_time("2026-06-07"):  # воскресенье
        response = client.get(f"/hello-world/{name}")
        assert response.status_code == 200

        text = response.data.decode("utf-8")
        # Убеждаемся, что ответ содержит приветствие для воскресенья.
        assert text == "Привет, Гость. Хорошего воскресенья!"