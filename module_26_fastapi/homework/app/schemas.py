from pydantic import BaseModel, ConfigDict, Field


class RecipeCreate(BaseModel):
    """
    Данные для создания рецепта.

    Attributes:
        title: Название рецепта.
        cooking_time: Время приготовления в минутах.
        ingredients: Список ингредиентов.
        description: Пошаговое или текстовое описание приготовления.
    """

    title: str = Field(
        min_length=1,
        max_length=200,
        examples=["Паста карбонара"],
        description="Название рецепта.",
    )

    cooking_time: int = Field(
        gt=0,
        le=1440,
        examples=[25],
        description="Время приготовления в минутах.",
    )

    ingredients: list[str] = Field(
        min_length=1,
        examples=[["Спагетти — 200 г", "Яйца — 2 шт.", "Бекон — 150 г"]],
        description="Непустой список ингредиентов.",
    )

    description: str = Field(
        min_length=1,
        examples=["Отварите пасту, обжарьте бекон и смешайте ингредиенты."],
        description="Подробное описание приготовления.",
    )


class RecipeShort(BaseModel):
    """
    Краткая информация о рецепте для экрана со списком.

    Attributes:
        id: Уникальный идентификатор рецепта.
        title: Название рецепта.
        views: Количество просмотров детального экрана.
        cooking_time: Время приготовления в минутах.
    """

    id: int
    title: str
    views: int
    cooking_time: int

    model_config = ConfigDict(from_attributes=True)


class RecipeDetail(RecipeShort):
    """
    Полная информация о рецепте для детального экрана.

    Attributes:
        ingredients: Список ингредиентов.
        description: Подробное описание приготовления.
    """

    ingredients: list[str]
    description: str