from datetime import UTC, datetime, timedelta

import pytest

from app import create_app
from models import Client, ClientParking, Parking, db as _db


@pytest.fixture()
def app():
    """
    Создаёт тестовое Flask-приложение и временную SQLite БД в памяти.
    """
    test_app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
        }
    )

    with test_app.app_context():
        _db.create_all()

        test_client = Client(
            name="Иван",
            surname="Иванов",
            credit_card="1111 2222 3333 4444",
            car_number="А123ВС77",
        )

        test_parking = Parking(
            address="Москва, Тверская, 1",
            opened=True,
            count_places=10,
            count_available_places=10,
        )

        log_client = Client(
            name="Пётр",
            surname="Петров",
            credit_card="2222 2222 2222 2222",
            car_number="В456КС77",
        )

        log_parking = Parking(
            address="Москва, Арбат, 10",
            opened=True,
            count_places=5,
            count_available_places=5,
        )

        _db.session.add_all(
            [
                test_client,
                test_parking,
                log_client,
                log_parking,
            ]
        )
        _db.session.commit()

        parking_log = ClientParking(
            client_id=log_client.id,
            parking_id=log_parking.id,
            time_in=datetime.now(UTC) - timedelta(hours=1),
            time_out=datetime.now(UTC),
        )

        _db.session.add(parking_log)
        _db.session.commit()

    yield test_app

    with test_app.app_context():
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    """
    Возвращает тестовый HTTP-клиент Flask.
    """
    return app.test_client()


@pytest.fixture()
def database(app):
    """
    Передаёт объект SQLAlchemy db в тест и поддерживает
    активный application context на протяжении теста.
    """
    with app.app_context():
        yield _db