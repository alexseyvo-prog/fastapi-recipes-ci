import sqlite3
from dataclasses import dataclass
from typing import Dict, List, Optional


DATABASE_NAME = 'table_books.db'
BOOKS_TABLE_NAME = 'books'
AUTHORS_TABLE_NAME = 'authors'


DATA = [
    {
        'id': 0,
        'title': 'A Byte of Python',
        'author': {
            'first_name': 'Swaroop',
            'last_name': 'C. H.',
            'middle_name': None,
        },
    },
    {
        'id': 1,
        'title': 'Moby-Dick; or, The Whale',
        'author': {
            'first_name': 'Herman',
            'last_name': 'Melville',
            'middle_name': None,
        },
    },
    {
        'id': 3,
        'title': 'War and Peace',
        'author': {
            'first_name': 'Leo',
            'last_name': 'Tolstoy',
            'middle_name': None,
        },
    },
]


@dataclass
class Author:
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    id: Optional[int] = None


@dataclass
class Book:
    title: str
    author_id: int
    id: Optional[int] = None
    author: Optional[Author] = None


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_NAME)
    connection.execute('PRAGMA foreign_keys = ON')
    return connection


def init_db(initial_records: List[Dict]) -> None:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.executescript(f"""
            DROP TABLE IF EXISTS {BOOKS_TABLE_NAME};
            DROP TABLE IF EXISTS {AUTHORS_TABLE_NAME};

            CREATE TABLE {AUTHORS_TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                middle_name TEXT
            );

            CREATE TABLE {BOOKS_TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                author_id INTEGER NOT NULL,

                FOREIGN KEY (author_id)
                    REFERENCES {AUTHORS_TABLE_NAME}(id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE
            );
        """)

        for record in initial_records:
            author_data = record['author']

            cursor.execute(f"""
                INSERT INTO {AUTHORS_TABLE_NAME}
                    (first_name, last_name, middle_name)
                VALUES (?, ?, ?)
            """, (
                author_data['first_name'],
                author_data['last_name'],
                author_data.get('middle_name'),
            ))

            author_id = cursor.lastrowid

            cursor.execute(f"""
                INSERT INTO {BOOKS_TABLE_NAME}
                    (id, title, author_id)
                VALUES (?, ?, ?)
            """, (
                record['id'],
                record['title'],
                author_id,
            ))


def get_author_by_id(author_id: int) -> Optional[Author]:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(f"""
            SELECT id, first_name, last_name, middle_name
            FROM {AUTHORS_TABLE_NAME}
            WHERE id = ?
        """, (author_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        return Author(
            id=row[0],
            first_name=row[1],
            last_name=row[2],
            middle_name=row[3],
        )


def get_author_books(author_id: int) -> Optional[tuple[Author, list[Book]]]:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(f"""
            SELECT id, first_name, last_name, middle_name
            FROM {AUTHORS_TABLE_NAME}
            WHERE id = ?
        """, (author_id,))

        author_row = cursor.fetchone()

        if author_row is None:
            return None

        author = Author(
            id=author_row[0],
            first_name=author_row[1],
            last_name=author_row[2],
            middle_name=author_row[3],
        )

        cursor.execute(f"""
            SELECT
                b.id,
                b.title,
                b.author_id,
                a.id,
                a.first_name,
                a.last_name,
                a.middle_name
            FROM {BOOKS_TABLE_NAME} AS b
            JOIN {AUTHORS_TABLE_NAME} AS a
                ON b.author_id = a.id
            WHERE b.author_id = ?
            ORDER BY b.id
        """, (author_id,))

        books = [
            _book_from_row(row)
            for row in cursor.fetchall()
        ]

        return author, books


def add_author(author: Author) -> Author:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(f"""
            INSERT INTO {AUTHORS_TABLE_NAME}
                (first_name, last_name, middle_name)
            VALUES (?, ?, ?)
        """, (
            author.first_name,
            author.last_name,
            author.middle_name,
        ))

        author.id = cursor.lastrowid

        return author


def delete_author_by_id(author_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(f"""
            DELETE FROM {AUTHORS_TABLE_NAME}
            WHERE id = ?
        """, (author_id,))

        return cursor.rowcount > 0


def _book_from_row(row: tuple) -> Book:
    return Book(
        id=row[0],
        title=row[1],
        author_id=row[2],
        author=Author(
            id=row[3],
            first_name=row[4],
            last_name=row[5],
            middle_name=row[6],
        ),
    )


def get_all_books() -> list[Book]:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(f"""
            SELECT
                b.id,
                b.title,
                b.author_id,
                a.id,
                a.first_name,
                a.last_name,
                a.middle_name
            FROM {BOOKS_TABLE_NAME} AS b
            JOIN {AUTHORS_TABLE_NAME} AS a
                ON b.author_id = a.id
            ORDER BY b.id
        """)

        return [
            _book_from_row(row)
            for row in cursor.fetchall()
        ]


def get_book_by_id(book_id: int) -> Optional[Book]:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(f"""
            SELECT
                b.id,
                b.title,
                b.author_id,
                a.id,
                a.first_name,
                a.last_name,
                a.middle_name
            FROM {BOOKS_TABLE_NAME} AS b
            JOIN {AUTHORS_TABLE_NAME} AS a
                ON b.author_id = a.id
            WHERE b.id = ?
        """, (book_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        return _book_from_row(row)


def get_book_by_title(
    title: str,
    exclude_id: Optional[int] = None,
) -> Optional[Book]:
    with get_connection() as connection:
        cursor = connection.cursor()

        if exclude_id is None:
            cursor.execute(f"""
                SELECT
                    b.id,
                    b.title,
                    b.author_id,
                    a.id,
                    a.first_name,
                    a.last_name,
                    a.middle_name
                FROM {BOOKS_TABLE_NAME} AS b
                JOIN {AUTHORS_TABLE_NAME} AS a
                    ON b.author_id = a.id
                WHERE b.title = ?
            """, (title,))
        else:
            cursor.execute(f"""
                SELECT
                    b.id,
                    b.title,
                    b.author_id,
                    a.id,
                    a.first_name,
                    a.last_name,
                    a.middle_name
                FROM {BOOKS_TABLE_NAME} AS b
                JOIN {AUTHORS_TABLE_NAME} AS a
                    ON b.author_id = a.id
                WHERE b.title = ?
                  AND b.id != ?
            """, (title, exclude_id))

        row = cursor.fetchone()

        if row is None:
            return None

        return _book_from_row(row)


def add_book(book: Book) -> Book:
    if get_author_by_id(book.author_id) is None:
        raise ValueError(
            f'Author with id {book.author_id} does not exist'
        )

    if get_book_by_title(book.title) is not None:
        raise ValueError(
            f'Book with title "{book.title}" already exists'
        )

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(f"""
            INSERT INTO {BOOKS_TABLE_NAME}
                (title, author_id)
            VALUES (?, ?)
        """, (
            book.title,
            book.author_id,
        ))

        book.id = cursor.lastrowid

    return get_book_by_id(book.id)


def update_book_by_id(book: Book) -> Optional[Book]:
    if get_author_by_id(book.author_id) is None:
        raise ValueError(
            f'Author with id {book.author_id} does not exist'
        )

    if get_book_by_title(book.title, exclude_id=book.id) is not None:
        raise ValueError(
            f'Book with title "{book.title}" already exists'
        )

    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(f"""
            UPDATE {BOOKS_TABLE_NAME}
            SET title = ?, author_id = ?
            WHERE id = ?
        """, (
            book.title,
            book.author_id,
            book.id,
        ))

        if cursor.rowcount == 0:
            return None

    return get_book_by_id(book.id)


def delete_book_by_id(book_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(f"""
            DELETE FROM {BOOKS_TABLE_NAME}
            WHERE id = ?
        """, (book_id,))

        return cursor.rowcount > 0