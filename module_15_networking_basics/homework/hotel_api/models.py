import sqlite3
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class Room:
    """Модель номера в отеле."""
    id: int
    floor: int
    beds: int
    guest_num: int
    price: int

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует номер в словарь."""
        return {
            "roomId": self.id,
            "floor": self.floor,
            "beds": self.beds,
            "guestNum": self.guest_num,
            "price": self.price,
        }


@dataclass
class Booking:
    """Модель бронирования."""
    id: int
    room_id: int
    check_in: int
    check_out: int
    first_name: str
    last_name: str

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует бронирование в словарь."""
        return {
            "bookingId": self.id,
            "roomId": self.room_id,
            "checkIn": self.check_in,
            "checkOut": self.check_out,
            "firstName": self.first_name,
            "lastName": self.last_name,
        }


def init_db() -> None:
    """Инициализирует базу данных."""
    with sqlite3.connect('hotel.db') as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                floor INTEGER NOT NULL,
                beds INTEGER NOT NULL,
                guest_num INTEGER NOT NULL,
                price INTEGER NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                check_in INTEGER NOT NULL,
                check_out INTEGER NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                FOREIGN KEY (room_id) REFERENCES rooms(id)
            )
        """)

        conn.commit()


def get_all_rooms() -> List[Room]:
    """Возвращает все номера."""
    with sqlite3.connect('hotel.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, floor, beds, guest_num, price FROM rooms")
        return [Room(*row) for row in cursor.fetchall()]


def get_room_by_id(room_id: int) -> Optional[Room]:
    """Возвращает номер по ID."""
    with sqlite3.connect('hotel.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, floor, beds, guest_num, price FROM rooms WHERE id = ?",
            (room_id,),
        )
        row = cursor.fetchone()
        return Room(*row) if row else None


def create_room(
    floor: int,
    beds: int,
    guest_num: int,
    price: int,
) -> Room:
    """Создаёт новый номер."""
    with sqlite3.connect('hotel.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO rooms (floor, beds, guest_num, price)
            VALUES (?, ?, ?, ?)
            """,
            (floor, beds, guest_num, price),
        )
        conn.commit()
        room_id = cursor.lastrowid
        return Room(room_id, floor, beds, guest_num, price)


def get_available_rooms(
    check_in: int,
    check_out: int,
    guests_num: int,
) -> List[Room]:
    """
    Возвращает доступные номера на указанные даты.

    Если в базе нет номеров — возвращает пустой список.
    Номер считается доступным, если:
    - у него достаточно мест (guest_num >= guests_num)
    - нет бронирований, пересекающихся с указанными датами
    """
    with sqlite3.connect('hotel.db') as conn:
        cursor = conn.cursor()

        # Получаем все номера с достаточным количеством мест
        cursor.execute(
            """
            SELECT id, floor, beds, guest_num, price
            FROM rooms
            WHERE guest_num >= ?
            """,
            (guests_num,),
        )
        all_rooms = [Room(*row) for row in cursor.fetchall()]

        # Если номеров нет — возвращаем пустой список
        if not all_rooms:
            return []

        # Получаем забронированные номера на эти даты
        cursor.execute(
            """
            SELECT DISTINCT room_id FROM bookings
            WHERE NOT (check_out <= ? OR check_in >= ?)
            """,
            (check_in, check_out),
        )
        booked_room_ids = {row[0] for row in cursor.fetchall()}

        # Возвращаем только незабронированные номера
        return [
            room for room in all_rooms
            if room.id not in booked_room_ids
        ]


def is_room_booked(
    room_id: int,
    check_in: int,
    check_out: int,
) -> bool:
    """
    Проверяет, забронирован ли номер на указанные даты.

    Если номер не существует — считаем, что он не забронирован.
    """
    # Проверяем, существует ли номер
    room = get_room_by_id(room_id)
    if room is None:
        # Номера нет в базе — считаем, что он не забронирован
        return False

    with sqlite3.connect('hotel.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) FROM bookings
            WHERE room_id = ?
            AND NOT (check_out <= ? OR check_in >= ?)
            """,
            (room_id, check_in, check_out),
        )
        count = cursor.fetchone()[0]
        return count > 0


def create_booking(
    room_id: int,
    check_in: int,
    check_out: int,
    first_name: str,
    last_name: str,
) -> Booking:
    """Создаёт бронирование."""
    with sqlite3.connect('hotel.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO bookings (room_id, check_in, check_out, first_name, last_name)
            VALUES (?, ?, ?, ?, ?)
            """,
            (room_id, check_in, check_out, first_name, last_name),
        )
        conn.commit()
        booking_id = cursor.lastrowid
        return Booking(
            booking_id,
            room_id,
            check_in,
            check_out,
            first_name,
            last_name,
        )