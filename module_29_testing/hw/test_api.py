from datetime import datetime

import pytest

from factories import ClientFactory, ParkingFactory
from models import Client, ClientParking, Parking, db


@pytest.mark.parametrize(
    "url",
    [
        "/clients",
        "/clients/1",
    ],
)
def test_get_methods_return_200(client, url):
    """
    Проверяет, что GET-запросы к API возвращают HTTP 200.

    Тест запускается дважды:
    - для получения всех клиентов;
    - для получения клиента с id=1.
    """
    response = client.get(url)

    assert response.status_code == 200


def test_create_client(client, app):
    """
    Проверяет создание нового клиента через POST /clients.

    Проверяются код ответа, содержимое JSON-ответа
    и наличие созданной записи в тестовой базе данных.
    """
    payload = {
        "name": "Пётр",
        "surname": "Петров",
        "credit_card": "5555 5555 5555 5555",
        "car_number": "М456ОР77",
    }

    response = client.post("/clients", json=payload)

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] is not None
    assert data["name"] == payload["name"]
    assert data["surname"] == payload["surname"]
    assert data["credit_card"] == payload["credit_card"]
    assert data["car_number"] == payload["car_number"]

    with app.app_context():
        created_client = db.session.get(Client, data["id"])

        assert created_client is not None
        assert created_client.name == payload["name"]
        assert created_client.surname == payload["surname"]
        assert created_client.credit_card == payload["credit_card"]
        assert created_client.car_number == payload["car_number"]


def test_create_parking(client, app):
    """
    Проверяет создание новой парковки через POST /parkings.

    Проверяются код ответа, данные парковки в JSON
    и сохранение парковки в базе данных.
    """
    payload = {
        "address": "Санкт-Петербург, Невский проспект, 10",
        "opened": True,
        "count_places": 20,
        "count_available_places": 20,
    }

    response = client.post("/parkings", json=payload)

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] is not None
    assert data["address"] == payload["address"]
    assert data["opened"] == payload["opened"]
    assert data["count_places"] == payload["count_places"]
    assert (
        data["count_available_places"]
        == payload["count_available_places"]
    )

    with app.app_context():
        created_parking = db.session.get(Parking, data["id"])

        assert created_parking is not None
        assert created_parking.address == payload["address"]
        assert created_parking.opened == payload["opened"]
        assert created_parking.count_places == payload["count_places"]
        assert (
            created_parking.count_available_places
            == payload["count_available_places"]
        )


@pytest.mark.parking
def test_enter_parking(client, app):
    """
    Проверяет заезд клиента на парковку.

    До запроса проверяется, что парковка открыта и имеет свободные места.
    После запроса проверяется создание записи ClientParking и уменьшение
    количества свободных мест на одно.
    """
    payload = {
        "client_id": 1,
        "parking_id": 1,
    }

    with app.app_context():
        parking_before = db.session.get(Parking, 1)

        assert parking_before is not None
        assert parking_before.opened is True

        available_places_before = parking_before.count_available_places

        assert available_places_before > 0

    response = client.post("/client_parkings", json=payload)

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] is not None
    assert data["client_id"] == payload["client_id"]
    assert data["parking_id"] == payload["parking_id"]
    assert data["time_in"] is not None
    assert data["time_out"] is None

    with app.app_context():
        parking_after = db.session.get(Parking, 1)
        parking_log = db.session.get(ClientParking, data["id"])

        assert (
            parking_after.count_available_places
            == available_places_before - 1
        )

        assert parking_log is not None
        assert parking_log.client_id == payload["client_id"]
        assert parking_log.parking_id == payload["parking_id"]
        assert parking_log.time_in is not None
        assert parking_log.time_out is None


@pytest.mark.parking
def test_leave_parking(client, app):
    """
    Проверяет выезд клиента с парковки.

    Сначала выполняется въезд, затем DELETE-запрос на выезд.
    Проверяются наличие карты у клиента, заполнение time_out,
    корректная последовательность времени и увеличение свободных мест.
    """
    payload = {
        "client_id": 1,
        "parking_id": 1,
    }

    enter_response = client.post("/client_parkings", json=payload)

    assert enter_response.status_code == 201

    parking_log_id = enter_response.get_json()["id"]

    with app.app_context():
        parking_before = db.session.get(Parking, 1)
        test_client = db.session.get(Client, 1)

        assert parking_before is not None
        assert test_client is not None
        assert test_client.credit_card is not None

        available_places_before = parking_before.count_available_places

    response = client.delete("/client_parkings", json=payload)

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == parking_log_id
    assert data["time_in"] is not None
    assert data["time_out"] is not None

    time_in = datetime.fromisoformat(data["time_in"])
    time_out = datetime.fromisoformat(data["time_out"])

    assert time_out >= time_in

    with app.app_context():
        parking_after = db.session.get(Parking, 1)
        parking_log = db.session.get(ClientParking, parking_log_id)

        assert (
            parking_after.count_available_places
            == available_places_before + 1
        )

        assert parking_log is not None
        assert parking_log.time_in is not None
        assert parking_log.time_out is not None
        assert parking_log.time_out >= parking_log.time_in


def test_create_client_with_factory(client, app):
    """
    Проверяет создание клиента с данными из ClientFactory.

    ClientFactory.build() генерирует случайные данные, но не сохраняет
    объект в БД. API самостоятельно создаёт клиента через POST /clients.
    """
    factory_client = ClientFactory.build()

    payload = {
        "name": factory_client.name,
        "surname": factory_client.surname,
        "credit_card": factory_client.credit_card,
        "car_number": factory_client.car_number,
    }

    with app.app_context():
        clients_before = db.session.query(Client).count()

    response = client.post("/clients", json=payload)

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] is not None
    assert data["name"] == payload["name"]
    assert data["surname"] == payload["surname"]
    assert data["credit_card"] == payload["credit_card"]
    assert data["car_number"] == payload["car_number"]

    with app.app_context():
        clients_after = db.session.query(Client).count()
        created_client = db.session.get(Client, data["id"])

        assert clients_after == clients_before + 1
        assert created_client is not None
        assert created_client.name == payload["name"]
        assert created_client.surname == payload["surname"]
        assert created_client.credit_card == payload["credit_card"]
        assert created_client.car_number == payload["car_number"]


def test_create_parking_with_factory(client, app):
    """
    Проверяет создание парковки с данными из ParkingFactory.

    LazyAttribute в фабрике гарантирует, что число свободных мест
    не превышает общее число мест на парковке.
    """
    factory_parking = ParkingFactory.build()

    payload = {
        "address": factory_parking.address,
        "opened": factory_parking.opened,
        "count_places": factory_parking.count_places,
        "count_available_places": factory_parking.count_available_places,
    }

    with app.app_context():
        parkings_before = db.session.query(Parking).count()

    response = client.post("/parkings", json=payload)

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] is not None
    assert data["address"] == payload["address"]
    assert data["opened"] == payload["opened"]
    assert data["count_places"] == payload["count_places"]
    assert (
        data["count_available_places"]
        == payload["count_available_places"]
    )

    with app.app_context():
        parkings_after = db.session.query(Parking).count()
        created_parking = db.session.get(Parking, data["id"])

        assert parkings_after == parkings_before + 1
        assert created_parking is not None
        assert created_parking.address == payload["address"]
        assert created_parking.opened == payload["opened"]
        assert created_parking.count_places == payload["count_places"]
        assert (
            created_parking.count_available_places
            == payload["count_available_places"]
        )