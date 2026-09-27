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
    """Создаёт таблицы при первом запуске приложения."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title="Recipe Book API",
    version="1.0.0",
    description=(
        "Асинхронное API кулинарной книги. "
        "Позволяет создавать рецепты, получать список рецептов "
        "и открывать детальную информацию."
    ),
    lifespan=lifespan,
)

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", include_in_schema=False)
async def get_recipes_page(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Главная HTML-страница со списком рецептов."""
    statement = select(Recipe).order_by(
        Recipe.views.desc(),
        Recipe.cooking_time.asc(),
    )

    result = await session.execute(statement)
    recipes = result.scalars().all()

    return templates.TemplateResponse(
        request=request,
        name="recipes.html",
        context={"recipes": recipes},
    )


@app.get(
    "/recipes",
    response_model=list[RecipeShort],
    summary="Получить список рецептов",
    description=(
        "Возвращает рецепты для главного экрана. "
        "Сначала идут самые популярные рецепты, затем — рецепты "
        "с меньшим временем приготовления при равном числе просмотров."
    ),
    tags=["recipes"],
)
async def get_recipes(
    session: AsyncSession = Depends(get_session),
) -> list[RecipeShort]:
    """Получить все рецепты, отсортированные по популярности."""
    statement = select(Recipe).order_by(
        Recipe.views.desc(),
        Recipe.cooking_time.asc(),
    )

    result = await session.execute(statement)
    recipes = result.scalars().all()

    return list(recipes)


@app.get(
    "/recipes/{recipe_id}",
    response_model=RecipeDetail,
    summary="Получить рецепт по идентификатору",
    description=(
        "Возвращает полную информацию о рецепте и увеличивает "
        "счётчик его просмотров на единицу."
    ),
    responses={
        404: {
            "description": "Рецепт с указанным идентификатором не найден.",
        }
    },
    tags=["recipes"],
)
async def get_recipe(
    recipe_id: int,
    session: AsyncSession = Depends(get_session),
) -> RecipeDetail:
    """Получить детальную информацию о рецепте."""
    recipe = await session.get(Recipe, recipe_id)

    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Рецепт не найден",
        )

    recipe.views += 1
    await session.commit()
    await session.refresh(recipe)

    return RecipeDetail(
        id=recipe.id,
        title=recipe.title,
        views=recipe.views,
        cooking_time=recipe.cooking_time,
        ingredients=json.loads(recipe.ingredients),
        description=recipe.description,
    )


@app.post(
    "/recipes",
    response_model=RecipeDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Создать рецепт",
    description=(
        "Создаёт новый рецепт. У нового рецепта количество просмотров "
        "всегда равно нулю."
    ),
    tags=["recipes"],
)
async def create_recipe(
    recipe_data: RecipeCreate,
    session: AsyncSession = Depends(get_session),
) -> RecipeDetail:
    """Создать новый рецепт в кулинарной книге."""
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

    return RecipeDetail(
        id=recipe.id,
        title=recipe.title,
        views=recipe.views,
        cooking_time=recipe.cooking_time,
        ingredients=json.loads(recipe.ingredients),
        description=recipe.description,
    )


@app.get("/recipes/{recipe_id}/page", include_in_schema=False)
async def get_recipe_page(
    recipe_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """HTML-страница с детальной информацией о рецепте."""
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