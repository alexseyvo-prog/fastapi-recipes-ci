from datetime import datetime

import pytest

from factories import ClientFactory, ParkingFactory
from models import Client, ClientParking, Parking


@pytest.mark.parametrize(
    "url",
    [
        "/clients",
        "/clients/1",
    ],
)
def test_get_methods_return_200(client, url):
    """Проверяет, что GET-методы API возвращают HTTP 200."""
    response = client.get(url)

    assert response.status_code == 200


def test_create_client(client, database):
    """Проверяет создание и сохранение клиента через POST /clients."""
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

    created_client = database.session.get(Client, data["id"])

    assert created_client is not None
    assert created_client.name == payload["name"]
    assert created_client.surname == payload["surname"]
    assert created_client.credit_card == payload["credit_card"]
    assert created_client.car_number == payload["car_number"]


def test_create_parking(client, database):
    """Проверяет создание и сохранение парковки через POST /parkings."""
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

    created_parking = database.session.get(Parking, data["id"])

    assert created_parking is not None
    assert created_parking.address == payload["address"]
    assert created_parking.opened == payload["opened"]
    assert created_parking.count_places == payload["count_places"]
    assert (
        created_parking.count_available_places
        == payload["count_available_places"]
    )


@pytest.mark.parking
def test_enter_parking(client, database):
    """Проверяет успешный заезд клиента и уменьшение числа свободных мест."""
    payload = {
        "client_id": 1,
        "parking_id": 1,
    }

    parking_before = database.session.get(Parking, payload["parking_id"])

    assert parking_before is not None

    available_places_before = parking_before.count_available_places

    response = client.post("/client_parkings", json=payload)

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] is not None
    assert data["client_id"] == payload["client_id"]
    assert data["parking_id"] == payload["parking_id"]
    assert data["time_in"] is not None
    assert data["time_out"] is None

    parking_after = database.session.get(Parking, payload["parking_id"])
    parking_log = database.session.get(ClientParking, data["id"])

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
def test_leave_parking(client, database):
    """Проверяет успешный выезд, заполнение time_out и возврат места."""
    payload = {
        "client_id": 1,
        "parking_id": 1,
    }

    enter_response = client.post("/client_parkings", json=payload)

    assert enter_response.status_code == 201

    parking_log_id = enter_response.get_json()["id"]

    parking_before = database.session.get(Parking, payload["parking_id"])
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

    parking_after = database.session.get(Parking, payload["parking_id"])
    parking_log = database.session.get(ClientParking, parking_log_id)

    assert (
        parking_after.count_available_places
        == available_places_before + 1
    )
    assert parking_log is not None
    assert parking_log.time_in is not None
    assert parking_log.time_out is not None
    assert parking_log.time_out >= parking_log.time_in


def test_create_client_with_factory(database):
    """Проверяет создание и сохранение клиента через ClientFactory."""
    clients_before = database.session.query(Client).count()

    new_client = ClientFactory()

    assert new_client.id is not None
    assert database.session.query(Client).count() == clients_before + 1


def test_create_parking_with_factory(database):
    """Проверяет создание и сохранение парковки через ParkingFactory."""
    parkings_before = database.session.query(Parking).count()

    new_parking = ParkingFactory()

    assert new_parking.id is not None
    assert new_parking.count_available_places <= new_parking.count_places
    assert database.session.query(Parking).count() == parkings_before + 1


@pytest.mark.parking
def test_enter_closed_parking(client, database):
    """Проверяет запрет въезда на закрытую парковку."""
    parking = ParkingFactory(
        opened=False,
        count_places=5,
        count_available_places=5,
    )
    new_client = ClientFactory()

    response = client.post(
        "/client_parkings",
        json={
            "client_id": new_client.id,
            "parking_id": parking.id,
        },
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Парковка закрыта."

    parking_after = database.session.get(Parking, parking.id)

    assert parking_after.count_available_places == 5

    parking_log = database.session.scalar(
        database.select(ClientParking).where(
            ClientParking.client_id == new_client.id,
            ClientParking.parking_id == parking.id,
        )
    )

    assert parking_log is None


@pytest.mark.parking
def test_enter_full_parking(client, database):
    """Проверяет запрет въезда на парковку без свободных мест."""
    parking = ParkingFactory(
        opened=True,
        count_places=5,
        count_available_places=0,
    )
    new_client = ClientFactory()

    response = client.post(
        "/client_parkings",
        json={
            "client_id": new_client.id,
            "parking_id": parking.id,
        },
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Нет свободных мест."

    parking_after = database.session.get(Parking, parking.id)

    assert parking_after.count_available_places == 0

    parking_log = database.session.scalar(
        database.select(ClientParking).where(
            ClientParking.client_id == new_client.id,
            ClientParking.parking_id == parking.id,
        )
    )

    assert parking_log is None


@pytest.mark.parking
def test_leave_parking_without_credit_card(client, database):
    """Проверяет запрет выезда, если у клиента нет привязанной карты."""
    parking = ParkingFactory(
        opened=True,
        count_places=5,
        count_available_places=5,
    )
    new_client = ClientFactory(credit_card=None)

    enter_response = client.post(
        "/client_parkings",
        json={
            "client_id": new_client.id,
            "parking_id": parking.id,
        },
    )

    assert enter_response.status_code == 201

    parking_log_id = enter_response.get_json()["id"]

    response = client.delete(
        "/client_parkings",
        json={
            "client_id": new_client.id,
            "parking_id": parking.id,
        },
    )

    assert response.status_code == 400
    assert (
        response.get_json()["error"]
        == "Нельзя произвести оплату: карта не привязана."
    )

    parking_log = database.session.get(ClientParking, parking_log_id)
    parking_after = database.session.get(Parking, parking.id)

    assert parking_log.time_out is None
    assert parking_after.count_available_places == 4


@pytest.mark.parking
def test_leave_parking_without_entering(client, database):
    """Проверяет, что нельзя выехать без активного заезда."""
    parking = ParkingFactory(
        opened=True,
        count_places=5,
        count_available_places=5,
    )
    new_client = ClientFactory(
        credit_card="5555 5555 5555 5555",
    )

    response = client.delete(
        "/client_parkings",
        json={
            "client_id": new_client.id,
            "parking_id": parking.id,
        },
    )

    assert response.status_code == 404
    assert (
        response.get_json()["error"]
        == "Активный въезд клиента на эту парковку не найден."
    )

    parking_after = database.session.get(Parking, parking.id)

    assert parking_after.count_available_places == 5