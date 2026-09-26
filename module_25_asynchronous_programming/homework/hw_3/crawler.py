import argparse
import asyncio
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

DEFAULT_DEPTH = 3
DEFAULT_CONCURRENCY = 10
OUTPUT_FILE = Path("external_links.txt")


def normalize_url(base_url: str, href: str) -> str | None:
    """Преобразует относительную ссылку в абсолютную и отбрасывает фрагмент #..."""
    if not href:
        return None

    absolute_url = urljoin(base_url, href)
    clean_url, _ = urldefrag(absolute_url)

    parsed = urlparse(clean_url)

    if parsed.scheme not in {"http", "https"}:
        return None

    if not parsed.netloc:
        return None

    return clean_url


def extract_external_links(page_url: str, html: str) -> set[str]:
    """Возвращает только ссылки на другие домены."""
    page_domain = urlparse(page_url).netloc
    soup = BeautifulSoup(html, "html.parser")

    external_links = set()

    for tag in soup.find_all("a", href=True):
        url = normalize_url(page_url, tag["href"])

        if url is None:
            continue

        if urlparse(url).netloc != page_domain:
            external_links.add(url)

    return external_links


async def fetch_page(
    session: aiohttp.ClientSession,
    url: str,
    semaphore: asyncio.Semaphore,
) -> tuple[str, str] | None:
    """Загружает HTML-страницу и возвращает пару URL, HTML."""
    try:
        async with semaphore:
            async with session.get(url, allow_redirects=True) as response:
                response.raise_for_status()

                content_type = response.headers.get("Content-Type", "")
                if "text/html" not in content_type:
                    return None

                html = await response.text()
                return str(response.url), html

    except (
        aiohttp.ClientError,
        asyncio.TimeoutError,
        UnicodeDecodeError,
    ) as error:
        print(f"Не удалось загрузить {url}: {error}")
        return None


async def crawl(
    start_urls: list[str],
    max_depth: int = DEFAULT_DEPTH,
    concurrency: int = DEFAULT_CONCURRENCY,
) -> set[str]:
    """
    Обходит страницы до max_depth уровней.

    depth=1: только стартовые страницы.
    depth=2: стартовые страницы и найденные на них внешние ссылки.
    depth=3: ещё один уровень ссылок.
    """
    visited_pages: set[str] = set()
    found_external_links: set[str] = set()
    urls_for_current_level = set(start_urls)

    timeout = aiohttp.ClientTimeout(total=20)
    semaphore = asyncio.Semaphore(concurrency)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; AsyncExternalLinkCrawler/1.0)"
        )
    }

    async with aiohttp.ClientSession(
        timeout=timeout,
        headers=headers,
    ) as session:
        for depth in range(1, max_depth + 1):
            urls_to_fetch = urls_for_current_level - visited_pages

            if not urls_to_fetch:
                break

            print(
                f"Уровень {depth}/{max_depth}: "
                f"обрабатывается страниц — {len(urls_to_fetch)}"
            )

            visited_pages.update(urls_to_fetch)

            tasks = [
                fetch_page(session, url, semaphore)
                for url in urls_to_fetch
            ]
            responses = await asyncio.gather(*tasks)

            urls_for_next_level: set[str] = set()

            for result in responses:
                if result is None:
                    continue

                page_url, html = result
                external_links = extract_external_links(page_url, html)

                found_external_links.update(external_links)
                urls_for_next_level.update(external_links)

            urls_for_current_level = urls_for_next_level

    return found_external_links


async def save_links(links: set[str], output_file: Path) -> None:
    """Сохраняет ссылки через стандартный open в отдельном потоке."""
    def write_to_disk_sync() -> None:
        with open(output_file, "w", encoding="utf-8") as file:
            for link in sorted(links):
                file.write(f"{link}\n")

    await asyncio.to_thread(write_to_disk_sync)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Асинхронный краулер внешних ссылок"
    )

    parser.add_argument(
        "urls",
        nargs="+",
        help="Одна или несколько стартовых ссылок",
    )

    parser.add_argument(
        "--depth",
        type=int,
        default=DEFAULT_DEPTH,
        help="Количество уровней обхода, по умолчанию 3",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_FILE,
        help="Файл для сохранения найденных ссылок",
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help="Максимум одновременных запросов, по умолчанию 10",
    )

    return parser.parse_args()


async def async_main() -> None:
    args = parse_args()

    if args.depth < 1:
        raise ValueError("--depth должен быть не меньше 1")

    if args.concurrency < 1:
        raise ValueError("--concurrency должен быть не меньше 1")

    start_urls = []

    for url in args.urls:
        normalized = normalize_url("", url)

        if normalized is None:
            print(f"Пропущен некорректный URL: {url}")
            continue

        start_urls.append(normalized)

    if not start_urls:
        raise ValueError("Не передано ни одной корректной стартовой ссылки")

    links = await crawl(
        start_urls=start_urls,
        max_depth=args.depth,
        concurrency=args.concurrency,
    )

    await save_links(links, args.output)

    print(f"\nНайдено внешних ссылок: {len(links)}")
    print(f"Результат записан в: {args.output.absolute()}")


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()