import random

import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from models import Client, Parking, db


fake = Faker("ru_RU")


class ClientFactory(SQLAlchemyModelFactory):
    """
    Создаёт тестовых клиентов с автоматически сгенерированными данными.
    """

    class Meta:
        model = Client
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"

    name = factory.Faker("first_name", locale="ru_RU")
    surname = factory.Faker("last_name", locale="ru_RU")

    # У клиента может быть карта или её может не быть.
    credit_card = factory.LazyFunction(
        lambda: random.choice([None, fake.credit_card_number()])
    )

    car_number = factory.Faker("bothify", text="?###??###")


class ParkingFactory(SQLAlchemyModelFactory):
    """
    Создаёт тестовые парковки со случайными параметрами.
    """

    class Meta:
        model = Parking
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"

    address = factory.Faker("address", locale="ru_RU")
    opened = factory.Faker("pybool")

    # Количество мест генерируется в диапазоне от 1 до 100.
    count_places = factory.Faker("random_int", min=1, max=100)

    # Свободных мест всегда от 0 до общего количества мест.
    count_available_places = factory.LazyAttribute(
        lambda parking: random.randint(0, parking.count_places)
    )