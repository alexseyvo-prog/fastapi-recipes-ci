from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Client(db.Model):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    credit_card: Mapped[str | None] = mapped_column(String(50), nullable=True)
    car_number: Mapped[str | None] = mapped_column(String(10), nullable=True)

    parking_logs: Mapped[list["ClientParking"]] = relationship(
        back_populates="client",
    )


class Parking(db.Model):
    __tablename__ = "parking"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    address: Mapped[str] = mapped_column(String(100), nullable=False)
    opened: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    count_places: Mapped[int] = mapped_column(Integer, nullable=False)
    count_available_places: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    parking_logs: Mapped[list["ClientParking"]] = relationship(
        back_populates="parking",
    )


class ClientParking(db.Model):
    __tablename__ = "client_parking"

    __table_args__ = (
        UniqueConstraint(
            "client_id",
            "parking_id",
            name="unique_client_parking",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    client_id: Mapped[int | None] = mapped_column(
        ForeignKey("client.id"),
        nullable=True,
    )
    parking_id: Mapped[int | None] = mapped_column(
        ForeignKey("parking.id"),
        nullable=True,
    )
    time_in: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    time_out: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    client: Mapped[Client | None] = relationship(
        back_populates="parking_logs",
    )
    parking: Mapped[Parking | None] = relationship(
        back_populates="parking_logs",
    )