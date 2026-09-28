import asyncio
from pathlib import Path

import aiohttp

URL = "https://cataas.com/cat"


def write_file(path: Path, content: bytes) -> None:
    with open(path, "wb") as file:
        file.write(content)


async def download_one(
    session: aiohttp.ClientSession,
    index: int,
    output_dir: Path,
    semaphore: asyncio.Semaphore,
) -> None:
    async with semaphore:
        async with session.get(URL) as response:
            response.raise_for_status()
            content = await response.read()

    await asyncio.to_thread(
        write_file,
        output_dir / f"cat_{index}.jpg",
        content,
    )


async def download_cats_async(count: int, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    timeout = aiohttp.ClientTimeout(total=60)
    semaphore = asyncio.Semaphore(20)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [
            download_one(session, index, output_dir, semaphore)
            for index in range(count)
        ]
        await asyncio.gather(*tasks)