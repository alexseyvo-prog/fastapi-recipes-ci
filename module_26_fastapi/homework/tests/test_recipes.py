from fastapi.testclient import TestClient

from app.main import app


def create_recipe(
    client: TestClient,
    title: str,
    cooking_time: int,
) -> dict:
    response = client.post(
        "/recipes",
        json={
            "title": title,
            "cooking_time": cooking_time,
            "ingredients": ["Тестовый ингредиент"],
            "description": "Тестовое описание.",
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_recipe() -> None:
    with TestClient(app) as client:
        recipe = create_recipe(client, "Тестовый суп", 30)

        assert recipe["id"] > 0
        assert recipe["title"] == "Тестовый суп"
        assert recipe["cooking_time"] == 30
        assert recipe["views"] == 0
        assert recipe["ingredients"] == ["Тестовый ингредиент"]


def test_get_recipe_increments_views() -> None:
    with TestClient(app) as client:
        recipe = create_recipe(client, "Открываемый рецепт", 15)
        recipe_id = recipe["id"]

        first_response = client.get(f"/recipes/{recipe_id}")
        second_response = client.get(f"/recipes/{recipe_id}")

        assert first_response.status_code == 200
        assert second_response.status_code == 200
        assert first_response.json()["views"] == 1
        assert second_response.json()["views"] == 2


def test_get_recipe_not_found() -> None:
    with TestClient(app) as client:
        response = client.get("/recipes/999999")

        assert response.status_code == 404
        assert response.json() == {"detail": "Рецепт не найден"}


def test_recipe_list_is_sorted_by_views_then_cooking_time() -> None:
    with TestClient(app) as client:
        slow_recipe = create_recipe(client, "Медленный рецепт", 60)
        fast_recipe = create_recipe(client, "Быстрый рецепт", 10)
        popular_recipe = create_recipe(client, "Популярный рецепт", 20)

        client.get(f"/recipes/{popular_recipe['id']}")
        client.get(f"/recipes/{popular_recipe['id']}")

        response = client.get("/recipes")

        assert response.status_code == 200

        recipes = response.json()
        recipe_ids = [recipe["id"] for recipe in recipes]

        assert recipe_ids.index(popular_recipe["id"]) < recipe_ids.index(
            fast_recipe["id"]
        )
        assert recipe_ids.index(fast_recipe["id"]) < recipe_ids.index(
            slow_recipe["id"]
        )