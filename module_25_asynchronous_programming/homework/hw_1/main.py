import asyncio
from pathlib import Path

import aiohttp

URL = "https://cataas.com/cat"

CATS_WE_WANT = 10
OUT_PATH = Path(__file__).parent / "cats"
OUT_PATH.mkdir(exist_ok=True, parents=True)
OUT_PATH = OUT_PATH.absolute()


def write_to_disk_sync(content: bytes, idx: int) -> None:
    """Синхронная запись изображения стандартным open()."""
    file_path = OUT_PATH / f"{idx}.jpg"

    with open(file_path, "wb") as file:
        file.write(content)


async def write_to_disk(content: bytes, idx: int) -> None:
    """Запуск блокирующей записи в отдельном потоке."""
    await asyncio.to_thread(write_to_disk_sync, content, idx)


async def get_cat(client: aiohttp.ClientSession, idx: int) -> bytes:
    async with client.get(URL) as response:
        response.raise_for_status()
        print(f"Котик {idx}: HTTP {response.status}")

        content = await response.read()
        await write_to_disk(content, idx)

        return content


async def get_all_cats() -> list[bytes]:
    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as client:
        tasks = [
            get_cat(client, index)
            for index in range(CATS_WE_WANT)
        ]
        return await asyncio.gather(*tasks)


def main() -> None:
    result = asyncio.run(get_all_cats())
    print(f"Скачано котиков: {len(result)}")


if __name__ == "__main__":
    main()