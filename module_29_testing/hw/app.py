from datetime import UTC, datetime

from flask import Flask, jsonify, request
from sqlalchemy.exc import IntegrityError

from models import Client, ClientParking, Parking, db


def client_to_dict(client: Client) -> dict:
    return {
        "id": client.id,
        "name": client.name,
        "surname": client.surname,
        "credit_card": client.credit_card,
        "car_number": client.car_number,
    }


def parking_to_dict(parking: Parking) -> dict:
    return {
        "id": parking.id,
        "address": parking.address,
        "opened": parking.opened,
        "count_places": parking.count_places,
        "count_available_places": parking.count_available_places,
    }


def client_parking_to_dict(client_parking: ClientParking) -> dict:
    return {
        "id": client_parking.id,
        "client_id": client_parking.client_id,
        "parking_id": client_parking.parking_id,
        "time_in": (
            client_parking.time_in.isoformat()
            if client_parking.time_in
            else None
        ),
        "time_out": (
            client_parking.time_out.isoformat()
            if client_parking.time_out
            else None
        ),
    }


def get_json_data() -> dict:
    """Возвращает JSON-тело запроса либо пустой словарь."""
    return request.get_json(silent=True) or {}


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI="sqlite:///parking.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)

    # Создаёт таблицы Client, Parking и ClientParking,
    # если они ещё отсутствуют в используемой базе данных.
    with app.app_context():
        db.create_all()

    @app.get("/clients")
    def get_clients():
        clients = db.session.scalars(
            db.select(Client).order_by(Client.id),
        ).all()

        return jsonify(
            clients=[client_to_dict(client) for client in clients],
        ), 200

    @app.get("/clients/<int:client_id>")
    def get_client(client_id: int):
        client = db.get_or_404(Client, client_id)

        return jsonify(client_to_dict(client)), 200

    @app.post("/clients")
    def create_client():
        data = get_json_data()

        name = (data.get("name") or "").strip()
        surname = (data.get("surname") or "").strip()

        if not name or not surname:
            return jsonify(
                error="Поля name и surname обязательны.",
            ), 400

        client = Client(
            name=name[:50],
            surname=surname[:50],
            credit_card=(data.get("credit_card") or "")[:50] or None,
            car_number=(data.get("car_number") or "")[:10] or None,
        )

        db.session.add(client)
        db.session.commit()

        return jsonify(client_to_dict(client)), 201

    @app.delete("/clients/<int:client_id>")
    def delete_client(client_id: int):
        client = db.get_or_404(Client, client_id)

        active_parking = db.session.scalar(
            db.select(ClientParking).where(
                ClientParking.client_id == client.id,
                ClientParking.time_out.is_(None),
            )
        )

        if active_parking is not None:
            return jsonify(
                error="Нельзя удалить клиента: он находится на парковке.",
            ), 409

        db.session.delete(client)
        db.session.commit()

        return "", 204

    @app.post("/parkings")
    def create_parking():
        data = get_json_data()

        address = (data.get("address") or "").strip()
        count_places = data.get("count_places")

        if not address:
            return jsonify(error="Поле address обязательно."), 400

        if not isinstance(count_places, int) or isinstance(count_places, bool):
            return jsonify(
                error="count_places должно быть целым числом.",
            ), 400

        if count_places < 0:
            return jsonify(
                error="count_places не может быть отрицательным.",
            ), 400

        available_places = data.get(
            "count_available_places",
            count_places,
        )

        if (
            not isinstance(available_places, int)
            or isinstance(available_places, bool)
            or available_places < 0
            or available_places > count_places
        ):
            return jsonify(
                error=(
                    "count_available_places должно быть целым числом "
                    "от 0 до count_places."
                ),
            ), 400

        opened = data.get("opened", True)

        if not isinstance(opened, bool):
            return jsonify(
                error="opened должно быть true или false.",
            ), 400

        parking = Parking(
            address=address[:100],
            opened=opened,
            count_places=count_places,
            count_available_places=available_places,
        )

        db.session.add(parking)
        db.session.commit()

        return jsonify(parking_to_dict(parking)), 201

    @app.post("/client_parkings")
    def enter_parking():
        data = get_json_data()

        client_id = data.get("client_id")
        parking_id = data.get("parking_id")

        if (
            not isinstance(client_id, int)
            or isinstance(client_id, bool)
            or not isinstance(parking_id, int)
            or isinstance(parking_id, bool)
        ):
            return jsonify(
                error="client_id и parking_id должны быть целыми числами.",
            ), 400

        client = db.get_or_404(Client, client_id)
        parking = db.get_or_404(Parking, parking_id)

        if parking.opened is not True:
            return jsonify(error="Парковка закрыта."), 400

        if parking.count_available_places <= 0:
            return jsonify(error="Нет свободных мест."), 400

        active_log = db.session.scalar(
            db.select(ClientParking).where(
                ClientParking.client_id == client.id,
                ClientParking.parking_id == parking.id,
                ClientParking.time_out.is_(None),
            )
        )

        if active_log is not None:
            return jsonify(
                error="Клиент уже находится на этой парковке.",
            ), 409

        parking_log = ClientParking(
            client=client,
            parking=parking,
            time_in=datetime.now(UTC),
        )

        parking.count_available_places -= 1
        db.session.add(parking_log)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

            return jsonify(
                error=(
                    "Для этого клиента уже существует запись "
                    "на данной парковке."
                ),
            ), 409

        return jsonify(client_parking_to_dict(parking_log)), 201

    @app.delete("/client_parkings")
    def leave_parking():
        data = get_json_data()

        client_id = data.get("client_id")
        parking_id = data.get("parking_id")

        if (
            not isinstance(client_id, int)
            or isinstance(client_id, bool)
            or not isinstance(parking_id, int)
            or isinstance(parking_id, bool)
        ):
            return jsonify(
                error="client_id и parking_id должны быть целыми числами.",
            ), 400

        client = db.get_or_404(Client, client_id)
        parking = db.get_or_404(Parking, parking_id)

        if not client.credit_card:
            return jsonify(
                error="Нельзя произвести оплату: карта не привязана.",
            ), 400

        parking_log = db.session.scalar(
            db.select(ClientParking).where(
                ClientParking.client_id == client.id,
                ClientParking.parking_id == parking.id,
                ClientParking.time_out.is_(None),
            )
        )

        if parking_log is None:
            return jsonify(
                error="Активный въезд клиента на эту парковку не найден.",
            ), 404

        parking_log.time_out = datetime.now(UTC)

        if parking.count_available_places < parking.count_places:
            parking.count_available_places += 1

        db.session.commit()

        return jsonify(client_parking_to_dict(parking_log)), 200

    return app


if __name__ == "__main__":
    create_app().run(debug=True)