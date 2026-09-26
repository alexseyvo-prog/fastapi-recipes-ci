from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

URL = "https://cataas.com/cat"


def download_one(index: int, output_dir: Path) -> None:
    response = requests.get(URL, timeout=60)
    response.raise_for_status()

    file_path = output_dir / f"cat_{index}.jpg"
    with open(file_path, "wb") as file:
        file.write(response.content)


def download_cats_threads(
    count: int,
    output_dir: Path,
    max_workers: int = 20,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(download_one, index, output_dir)
            for index in range(count)
        ]

        for future in futures:
            future.result()