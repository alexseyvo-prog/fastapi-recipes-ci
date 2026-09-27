import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base, engine, get_session
from app.models import Recipe
from app.schemas import RecipeCreate, RecipeDetail, RecipeShort


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """
    Инициализирует приложение.

    При старте создаёт таблицы базы данных, если они ещё не существуют.
    При остановке освобождает подключения к базе данных.
    """
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


tags_metadata = [
    {
        "name": "recipes",
        "description": """
Операции с рецептами.

Фронтенд использует эти API-эндпоинты для создания рецептов, вывода
таблицы рецептов и показа детальной карточки выбранного рецепта.

### Правила сортировки

`GET /recipes` возвращает записи в следующем порядке:

1. `views` — по убыванию.
2. `cooking_time` — по возрастанию при одинаковом числе просмотров.

### Правило просмотров

Каждый успешный запрос `GET /recipes/{recipe_id}` увеличивает `views`
на 1 и возвращает уже обновлённое значение.
""",
    },
]


app = FastAPI(
    title="Recipe Book API",
    summary="Backend-сервис кулинарной книги.",
    version="1.0.0",
    description="""
## Назначение

API кулинарной книги хранит рецепты и предоставляет данные для
пользовательского интерфейса.

## Что должен делать фронтенд

1. На главной странице вызвать `GET /recipes`.
2. Вывести таблицу с полями `title`, `views`, `cooking_time`.
3. При переходе к рецепту вызвать `GET /recipes/{recipe_id}`.
4. Показать полную карточку рецепта: название, время готовки,
   ингредиенты и описание.
5. Для добавления рецепта отправить `POST /recipes`.

## Кодировка

Все запросы и ответы используют JSON в кодировке UTF-8.
Для заголовка запроса указывайте:

```text
Content-Type: application/json
```

## Статусы ответа

- `200 OK` — запрос успешно обработан.
- `201 Created` — рецепт успешно создан.
- `404 Not Found` — рецепт с указанным `id` не существует.
- `422 Unprocessable Entity` — данные запроса не прошли валидацию.
""",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def recipe_to_detail(recipe: Recipe) -> RecipeDetail:
    """
    Преобразует ORM-модель Recipe в полную модель ответа API.

    Поле ingredients хранится в SQLite как JSON-строка и перед отправкой
    клиенту преобразуется в список строк.
    """
    return RecipeDetail(
        id=recipe.id,
        title=recipe.title,
        views=recipe.views,
        cooking_time=recipe.cooking_time,
        ingredients=json.loads(recipe.ingredients),
        description=recipe.description,
    )


async def get_sorted_recipes(session: AsyncSession) -> list[Recipe]:
    """
    Возвращает рецепты в порядке, нужном для главной страницы.

    Сначала более просматриваемые рецепты, затем более быстрые.
    """
    statement = select(Recipe).order_by(
        Recipe.views.desc(),
        Recipe.cooking_time.asc(),
    )
    result = await session.execute(statement)
    return list(result.scalars().all())


@app.get(
    "/",
    include_in_schema=False,
)
async def get_recipes_page(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    Возвращает главную HTML-страницу.

    Пользователь видит таблицу: название, просмотры и время готовки.
    API-фронтенд должен использовать `GET /recipes`, который возвращает JSON.
    """
    recipes = await get_sorted_recipes(session)

    return templates.TemplateResponse(
        request=request,
        name="recipes.html",
        context={"recipes": recipes},
    )


@app.get(
    "/recipes",
    response_model=list[RecipeShort],
    status_code=status.HTTP_200_OK,
    summary="Получить список рецептов",
    description="""
Возвращает краткие данные всех рецептов для главной страницы.

Каждый объект содержит:

- `id` — идентификатор для открытия рецепта;
- `title` — название;
- `views` — количество просмотров;
- `cooking_time` — время приготовления в минутах.

Поля `ingredients` и `description` намеренно не возвращаются:
для карточки рецепта используйте `GET /recipes/{recipe_id}`.

Сортировка: сначала `views` по убыванию, затем `cooking_time`
по возрастанию при одинаковом количестве просмотров.
""",
    response_description="Массив кратких данных рецептов в заданном порядке.",
    tags=["recipes"],
)
async def get_recipes(
    session: AsyncSession = Depends(get_session),
) -> list[RecipeShort]:
    """Получить список рецептов в JSON-формате."""
    recipes = await get_sorted_recipes(session)
    return list(recipes)


@app.get(
    "/recipes/{recipe_id}",
    response_model=RecipeDetail,
    status_code=status.HTTP_200_OK,
    summary="Получить детальную информацию о рецепте",
    description="""
Возвращает полную информацию об одном рецепте.

Параметр `recipe_id` — положительный целочисленный идентификатор
из ответа `GET /recipes`.

**Важно:** каждый успешный запрос увеличивает `views` на 1.
Используйте число `views` из ответа, так как это актуальное значение
после открытия детальной карточки.
""",
    response_description="Полная информация о рецепте с обновлённым количеством просмотров.",
    responses={
        404: {
            "description": "Рецепт с указанным идентификатором не найден.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Рецепт не найден",
                    }
                }
            },
        }
    },
    tags=["recipes"],
)
async def get_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
) -> RecipeDetail:
    """Получить рецепт, увеличить просмотры и вернуть актуальные данные."""
    recipe = await session.get(Recipe, recipe_id)

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Рецепт не найден",
        )

    recipe.views += 1
    await session.commit()
    await session.refresh(recipe)

    return recipe_to_detail(recipe)


@app.post(
    "/recipes",
    response_model=RecipeDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Создать рецепт",
    description="""
Создаёт новый рецепт.

В тело запроса передаются:

- `title` — название;
- `cooking_time` — положительное число минут;
- `ingredients` — непустой список ингредиентов;
- `description` — текстовое описание.

Не передавайте `id` и `views`: сервер сам назначит идентификатор,
а количество просмотров у нового рецепта всегда равно `0`.
""",
    response_description="Созданный рецепт с серверным id и значением views: 0.",
    responses={
        422: {
            "description": "В теле запроса отсутствует обязательное поле или нарушены ограничения модели.",
        }
    },
    tags=["recipes"],
)
async def create_recipe(
    recipe_data: RecipeCreate,
    session: AsyncSession = Depends(get_session),
) -> RecipeDetail:
    """Создать рецепт и вернуть полную информацию о нём."""
    recipe = Recipe(
        title=recipe_data.title,
        cooking_time=recipe_data.cooking_time,
        ingredients=json.dumps(recipe_data.ingredients, ensure_ascii=False),
        description=recipe_data.description,
        views=0,
    )

    session.add(recipe)
    await session.commit()
    await session.refresh(recipe)

    return recipe_to_detail(recipe)


@app.get(
    "/recipes/{recipe_id}/page",
    include_in_schema=False,
)
async def get_recipe_page(
    recipe_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    Возвращает HTML-страницу рецепта.

    При каждом открытии увеличивает количество просмотров на 1.
    Данный маршрут предназначен для серверного HTML-интерфейса;
    SPA/фронтенду следует использовать JSON-маршрут
    `GET /recipes/{recipe_id}`.
    """
    recipe = await session.get(Recipe, recipe_id)

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Рецепт не найден",
        )

    recipe.views += 1
    await session.commit()
    await session.refresh(recipe)

    return templates.TemplateResponse(
        request=request,
        name="recipe_detail.html",
        context={
            "recipe": recipe,
            "ingredients": json.loads(recipe.ingredients),
        },
    )