from pydantic import BaseModel, ConfigDict, Field


class RecipeBase(BaseModel):
    """Общие поля рецепта, которые доступны клиентскому приложению."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Название рецепта.",
        examples=["Окрошка"],
    )
    cooking_time: int = Field(
        ...,
        gt=0,
        le=1440,
        description="Время приготовления в минутах. Должно быть больше нуля.",
        examples=[25],
    )


class RecipeShort(RecipeBase):
    """
    Краткая модель рецепта для списка.

    Возвращается в `GET /recipes`. Содержит ровно те данные,
    которые нужны для карточки или строки таблицы на главной странице.
    """

    id: int = Field(
        ...,
        description="Уникальный идентификатор рецепта.",
        examples=[1],
    )
    views: int = Field(
        ...,
        ge=0,
        description="Количество открытий детальной страницы рецепта.",
        examples=[12],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "title": "Окрошка",
                    "views": 12,
                    "cooking_time": 25,
                }
            ]
        },
    )


class RecipeCreate(RecipeBase):
    """
    Модель тела запроса для создания рецепта.

    Передаётся в `POST /recipes`. Поля `id` и `views` передавать не нужно:
    идентификатор создаёт сервер, а количество просмотров для нового рецепта
    всегда равно нулю.
    """

    ingredients: list[str] = Field(
        ...,
        min_length=1,
        description="Список ингредиентов. В списке должен быть хотя бы один элемент.",
        examples=[["Кефир", "Огурец", "Яйцо"]],
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Подробный текст приготовления или описание блюда.",
        examples=["Холодный суп на кефире с овощами."],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Окрошка",
                    "cooking_time": 25,
                    "ingredients": ["Кефир", "Огурец", "Яйцо"],
                    "description": "Холодный суп на кефире с овощами.",
                }
            ]
        },
    )


class RecipeDetail(RecipeShort):
    """
    Полная модель рецепта.

    Возвращается после создания рецепта и при запросе одного рецепта:
    `POST /recipes` и `GET /recipes/{recipe_id}`.
    """

    ingredients: list[str] = Field(
        ...,
        description="Список ингредиентов рецепта.",
        examples=[["Кефир", "Огурец", "Яйцо"]],
    )
    description: str = Field(
        ...,
        description="Подробное описание рецепта.",
        examples=["Холодный суп на кефире с овощами."],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "title": "Окрошка",
                    "views": 1,
                    "cooking_time": 25,
                    "ingredients": ["Кефир", "Огурец", "Яйцо"],
                    "description": "Холодный суп на кефире с овощами.",
                }
            ]
        },
    )
