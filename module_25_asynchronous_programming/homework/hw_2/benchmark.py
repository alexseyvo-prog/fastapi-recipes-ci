import asyncio
import shutil
import time
from pathlib import Path

from asyncio_cats import download_cats_async
from processes_cats import download_cats_processes
from threads_cats import download_cats_threads

COUNTS = (10, 50, 100)
BASE_DIR = Path(__file__).parent / "results"


def clean_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)

    path.mkdir(parents=True, exist_ok=True)


def measure(function, *args) -> float:
    start = time.perf_counter()
    function(*args)
    return time.perf_counter() - start


def measure_async(count: int, output_dir: Path) -> float:
    start = time.perf_counter()
    asyncio.run(download_cats_async(count, output_dir))
    return time.perf_counter() - start


def markdown_table(rows: list[dict]) -> str:
    lines = [
        "| Подход | Картинок | Время, сек | Файлов сохранено | Статус |",
        "|---|---:|---:|---:|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['approach']} | {row['count']} | "
            f"{row['seconds']:.2f} | {row['files']} | {row['status']} |"
        )

    return "\n".join(lines)


def run_test(
    approach: str,
    count: int,
    function,
    is_async: bool = False,
) -> dict:
    output_dir = BASE_DIR / approach / str(count)
    clean_directory(output_dir)

    if is_async:
        seconds = measure_async(count, output_dir)
    else:
        seconds = measure(function, count, output_dir)

    files_count = len(list(output_dir.glob("*.jpg")))
    status = "OK" if files_count == count else "ERROR"

    return {
        "approach": approach,
        "count": count,
        "seconds": seconds,
        "files": files_count,
        "status": status,
    }


def main() -> None:
    results = []

    for count in COUNTS:
        results.append(
            run_test(
                approach="asyncio + open/to_thread",
                count=count,
                function=download_cats_async,
                is_async=True,
            )
        )

        results.append(
            run_test(
                approach="threads",
                count=count,
                function=download_cats_threads,
            )
        )

        results.append(
            run_test(
                approach="processes",
                count=count,
                function=download_cats_processes,
            )
        )

    table = markdown_table(results)
    print(table)

    report_path = BASE_DIR / "benchmark_results.md"
    report_path.write_text(table, encoding="utf-8")

    print(f"\nОтчёт сохранён: {report_path}")


if __name__ == "__main__":
    main()