from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import requests

URL = "https://cataas.com/cat"


def download_one(index: int, output_dir: str) -> None:
    response = requests.get(URL, timeout=60)
    response.raise_for_status()

    file_path = Path(output_dir) / f"cat_{index}.jpg"
    with open(file_path, "wb") as file:
        file.write(response.content)


def download_cats_processes(
    count: int,
    output_dir: Path,
    max_workers: int = 10,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(download_one, index, str(output_dir))
            for index in range(count)
        ]

        for future in futures:
            future.result()