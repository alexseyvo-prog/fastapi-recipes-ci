import random

import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from models import Client, Parking, db


fake = Faker("ru_RU")


class ClientFactory(SQLAlchemyModelFactory):
    """
    Создаёт и сохраняет тестовых клиентов в тестовой БД.
    """

    class Meta:
        model = Client
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"

    name = factory.Faker("first_name", locale="ru_RU")
    surname = factory.Faker("last_name", locale="ru_RU")

    # У клиента случайным образом может быть карта или не быть карты.
    credit_card = factory.LazyFunction(
        lambda: random.choice([None, fake.credit_card_number()])
    )

    car_number = factory.Faker("bothify", text="?###??###")


class ParkingFactory(SQLAlchemyModelFactory):
    """
    Создаёт и сохраняет тестовые парковки в тестовой БД.
    """

    class Meta:
        model = Parking
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"

    address = factory.Faker("address", locale="ru_RU")
    opened = factory.Faker("pybool")
    count_places = factory.Faker("random_int", min=1, max=100)

    # Значение зависит от count_places и не может быть больше него.
    count_available_places = factory.LazyAttribute(
        lambda parking: random.randint(0, parking.count_places)
    )