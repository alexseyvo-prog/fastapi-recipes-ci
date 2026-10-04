from datetime import UTC, datetime, timedelta

import pytest

from app import create_app
from models import Client, ClientParking, Parking, db


@pytest.fixture()
def app():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
        }
    )

    with app.app_context():
        db.create_all()

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

        db.session.add_all([
            test_client,
            test_parking,
            log_client,
            log_parking,
        ])
        db.session.commit()

        parking_log = ClientParking(
            client_id=log_client.id,
            parking_id=log_parking.id,
            time_in=datetime.now(UTC) - timedelta(hours=1),
            time_out=datetime.now(UTC),
        )

        db.session.add(parking_log)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def database(app):
    with app.app_context():
        yield db