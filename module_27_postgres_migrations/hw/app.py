import os
import random

import requests
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Integer, String, func, select
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


USERS_URL = "https://dummyjson.com/users?limit=10"
COFFEE_URL = "https://dummyjson.com/products/search?q=coffee"

REQUIRED_RECORDS_COUNT = 10
SEED_LOCK_ID = 123


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Coffee(db.Model):
    """Сорт кофе из таблицы coffee."""

    __tablename__ = "coffee"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    reviews: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        nullable=True,
    )

    users: Mapped[list["User"]] = relationship(
        back_populates="coffee",
    )


class User(db.Model):
    """Пользователь и предпочитаемый им кофе."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str | None] = mapped_column(String(50), nullable=True)
    patronymic: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    address: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    coffee_id: Mapped[int | None] = mapped_column(
        ForeignKey("coffee.id"),
        nullable=True,
    )

    coffee: Mapped[Coffee | None] = relationship(
        back_populates="users",
    )


def coffee_to_dict(coffee: Coffee) -> dict:
    """Преобразует ORM-объект Coffee в JSON-совместимый словарь."""
    return {
        "id": coffee.id,
        "title": coffee.title,
        "category": coffee.category,
        "description": coffee.description,
        "reviews": coffee.reviews,
    }


def user_to_dict(user: User) -> dict:
    """Преобразует ORM-объект User в JSON-ответ вместе с его кофе."""
    return {
        "id": user.id,
        "name": user.name,
        "surname": user.surname,
        "patronymic": user.patronymic,
        "address": user.address,
        "coffee_id": user.coffee_id,
        "coffee": coffee_to_dict(user.coffee) if user.coffee else None,
    }


def load_coffees() -> list[Coffee]:
    """Получает данные о кофе и создаёт ровно десять ORM-объектов."""
    response = requests.get(COFFEE_URL, timeout=20)
    response.raise_for_status()

    products = response.json().get("products", [])

    if not products:
        raise RuntimeError("DummyJSON не вернул ни одного товара по coffee.")

    coffees: list[Coffee] = []

    for index in range(REQUIRED_RECORDS_COUNT):
        product = products[index % len(products)]

        reviews = [
            review["comment"]
            for review in product.get("reviews", [])
            if review.get("comment")
        ]

        coffees.append(
            Coffee(
                title=f"{product['title']} #{index + 1}"[:200],
                category=product.get("category"),
                description=product.get("description"),
                reviews=reviews or None,
            )
        )

    return coffees


def load_users(coffees: list[Coffee]) -> list[User]:
    """Получает десять пользователей и назначает каждому случайный кофе."""
    response = requests.get(USERS_URL, timeout=20)
    response.raise_for_status()

    api_users = response.json().get("users", [])

    if len(api_users) < REQUIRED_RECORDS_COUNT:
        raise RuntimeError(
            "DummyJSON вернул меньше 10 пользователей: "
            f"{len(api_users)}."
        )

    users: list[User] = []

    for api_user in api_users[:REQUIRED_RECORDS_COUNT]:
        users.append(
            User(
                name=api_user.get("firstName", "")[:50],
                surname=api_user.get("lastName", "")[:50] or None,
                address=api_user.get("address"),
                coffee=random.choice(coffees),
            )
        )

    return users


def seed_database() -> None:
    """Один раз заполняет полностью пустую БД десятью кофе и пользователями."""
    with db.session.begin():
        db.session.execute(func.pg_advisory_xact_lock(SEED_LOCK_ID))

        coffee_exists = db.session.query(Coffee.id).first() is not None
        user_exists = db.session.query(User.id).first() is not None

        if coffee_exists or user_exists:
            return

        coffees = load_coffees()
        db.session.add_all(coffees)
        db.session.flush()

        db.session.add_all(load_users(coffees))


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["DATABASE_SEEDED"] = False

    db.init_app(app)

    @app.before_request
    def seed_on_first_request():
        if app.config["DATABASE_SEEDED"]:
            return

        try:
            seed_database()
        except Exception:
            db.session.rollback()
            raise
        else:
            app.config["DATABASE_SEEDED"] = True

    @app.get("/")
    def index():
        return jsonify(
            message="Flask подключён к skillbox_db",
            coffees_count=db.session.query(Coffee).count(),
            users_count=db.session.query(User).count(),
        )

    @app.post("/users")
    def create_user():
        data = request.get_json(silent=True) or {}

        name = data.get("name", "").strip()
        coffee_id = data.get("coffee_id")

        if not name:
            return jsonify(error="Поле name обязательно."), 400

        if not coffee_id:
            return jsonify(error="Поле coffee_id обязательно."), 400

        coffee = db.session.get(Coffee, coffee_id)

        if coffee is None:
            return jsonify(error="Кофе с таким coffee_id не найден."), 404

        user = User(
            name=name[:50],
            surname=(data.get("surname") or "")[:50] or None,
            patronymic=(data.get("patronymic") or "")[:50] or None,
            address=data.get("address"),
            coffee=coffee,
        )

        db.session.add(user)
        db.session.commit()

        return jsonify(user_to_dict(user)), 201

    @app.get("/coffees/search")
    def search_coffee():
        title = request.args.get("title", "").strip()

        if not title:
            return jsonify(error="Передайте параметр title."), 400

        search_vector = func.to_tsvector("simple", Coffee.title)
        search_query = func.plainto_tsquery("simple", title)

        coffees = db.session.scalars(
            select(Coffee)
            .where(search_vector.op("@@")(search_query))
            .order_by(Coffee.id)
        ).all()

        return jsonify(
            count=len(coffees),
            coffees=[coffee_to_dict(coffee) for coffee in coffees],
        )

    @app.get("/coffees/reviews")
    def unique_reviews():
        review = func.unnest(Coffee.reviews).label("review")

        reviews = db.session.scalars(
            select(review)
            .where(Coffee.reviews.is_not(None))
            .distinct()
            .order_by(review)
        ).all()

        return jsonify(
            count=len(reviews),
            reviews=reviews,
        )

    @app.get("/users/by-country")
    def users_by_country():
        country = request.args.get("country", "").strip()

        if not country:
            return jsonify(error="Передайте параметр country."), 400

        users = db.session.scalars(
            select(User)
            .where(User.address["country"].as_string() == country)
            .order_by(User.id)
        ).all()

        return jsonify(
            country=country,
            count=len(users),
            users=[user_to_dict(user) for user in users],
        )

    return app


app = create_app()