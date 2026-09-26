import asyncio
from pathlib import Path

import aiohttp

URL = "https://cataas.com/cat"
CATS_WE_WANT = 10

OUT_PATH = Path(__file__).parent / "cats"
OUT_PATH.mkdir(exist_ok=True, parents=True)
OUT_PATH = OUT_PATH.absolute()


def write_to_disk_sync(content: bytes, idx: int) -> None:
    file_path = OUT_PATH / f"{idx}.png"

    with open(file_path, "wb") as file:
        file.write(content)


async def write_to_disk(content: bytes, idx: int) -> None:
    await asyncio.to_thread(write_to_disk_sync, content, idx)


async def get_cat(client: aiohttp.ClientSession, idx: int) -> None:
    async with client.get(URL) as response:
        response.raise_for_status()
        print(response.status)

        content = await response.read()
        await write_to_disk(content, idx)


async def get_all_cats() -> list[None]:
    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as client:
        tasks = [get_cat(client, i) for i in range(CATS_WE_WANT)]
        return await asyncio.gather(*tasks)


def main() -> None:
    result = asyncio.run(get_all_cats())
    print(len(result))


if __name__ == "__main__":
    main()