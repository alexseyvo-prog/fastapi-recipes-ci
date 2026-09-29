import os
import random

import requests
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, ForeignKey, Integer, String, func, select
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


USERS_URL = "https://dummyjson.com/users?limit=10"
COFFEE_URL = "https://dummyjson.com/products/search?q=coffee"

REQUIRED_RECORDS_COUNT = 10


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
    patronymic: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # has_sale: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
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
        "has_sale": user.has_sale,
        "address": user.address,
        "coffee_id": user.coffee_id,
        "coffee": coffee_to_dict(user.coffee) if user.coffee else None,
    }


def load_coffees() -> list[Coffee]:
    """
    Получает товары по ссылке из задания и создаёт 10 записей кофе.

    DummyJSON сейчас возвращает меньше 10 результатов по coffee, поэтому
    найденные товары повторяются циклически с уникальным номером в title.
    """
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

        title = f"{product['title']} #{index + 1}"

        coffees.append(
            Coffee(
                title=title[:200],
                category=product.get("category"),
                description=product.get("description"),
                reviews=reviews or None,
            )
        )

    return coffees


def load_users(coffees: list[Coffee]) -> list[User]:
    """Получает десять пользователей и назначает им случайный кофе."""
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
        name = (
            f"{api_user.get('firstName', '')} "
            f"{api_user.get('lastName', '')}"
        ).strip()

        users.append(
            User(
                name=name[:50],
                has_sale=random.choice([True, False]),
                address=api_user.get("address"),
                coffee=random.choice(coffees),
            )
        )

    return users


def seed_database() -> None:
    """
    Гарантирует в БД ровно десять кофе и десять пользователей.

    При неверном количестве удаляет прежние записи и загружает новые.
    """
    coffee_count = db.session.query(Coffee).count()
    user_count = db.session.query(User).count()

    if (
        coffee_count == REQUIRED_RECORDS_COUNT
        and user_count == REQUIRED_RECORDS_COUNT
    ):
        return

    db.session.query(User).delete()
    db.session.query(Coffee).delete()
    db.session.commit()

    coffees = load_coffees()
    db.session.add_all(coffees)
    db.session.flush()

    users = load_users(coffees)
    db.session.add_all(users)
    db.session.commit()


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    @app.get("/")
    def index():
        return jsonify(
            message="Flask подключён к skillbox_db",
            coffees_count=db.session.query(Coffee).count(),
            users_count=db.session.query(User).count(),
        )

    @app.post("/users")
    def create_user():
        """
        Создаёт пользователя.

        Пример JSON-тела:
        {
            "name": "Иван Иванов",
            "has_sale": true,
            "address": {
                "country": "Russia",
                "city": "Moscow"
            },
            "coffee_id": 3
        }
        """
        data = request.get_json(silent=True) or {}

        name = data.get("name")
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
            has_sale=data.get("has_sale"),
            address=data.get("address"),
            coffee=coffee,
        )

        db.session.add(user)
        db.session.commit()

        return jsonify(user_to_dict(user)), 201

    @app.get("/coffees/search")
    def search_coffee():
        """
        Ищет кофе по title с помощью полнотекстового поиска PostgreSQL.

        Пример:
        GET /coffees/search?title=nescafe
        """
        title = request.args.get("title", "").strip()

        if not title:
            return jsonify(error="Передайте параметр title."), 400

        search_vector = func.to_tsvector(
            "simple",
            Coffee.title,
        )
        search_query = func.plainto_tsquery(
            "simple",
            title,
        )

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
        """
        Возвращает все уникальные элементы массивов coffee.reviews.
        """
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
        """
        Возвращает пользователей, у которых address.country совпадает
        с параметром country.

        Пример:
        GET /users/by-country?country=United%20States
        """
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

    # with app.app_context():
    #     # db.create_all()
    #     seed_database()

    return app


app = create_app()