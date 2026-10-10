from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Recipe(Base):
    """
    Рецепт в кулинарной книге.

    Attributes:
        id: Уникальный идентификатор рецепта.
        title: Название рецепта.
        cooking_time: Время приготовления в минутах.
        ingredients: Ингредиенты, записанные текстом.
        description: Подробное описание приготовления.
        views: Число открытий детальной страницы рецепта.
    """

    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    cooking_time: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    ingredients: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    views: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
