from typing import List, Dict, Any, Optional

from models import (
    Room,
    Booking,
    get_all_rooms,
    get_room_by_id,
    create_room,
    get_available_rooms,
    is_room_booked,
    create_booking,
)


class RoomService:
    """Бизнес-логика для работы с номерами."""

    @staticmethod
    def list_rooms() -> List[Dict[str, Any]]:
        """Возвращает все номера."""
        rooms = get_all_rooms()
        return [room.to_dict() for room in rooms]

    @staticmethod
    def add_room(
        floor: int,
        beds: int,
        guest_num: int,
        price: int,
    ) -> Dict[str, Any]:
        """Добавляет новый номер."""
        room = create_room(
            floor=floor,
            beds=beds,
            guest_num=guest_num,
            price=price,
        )
        return room.to_dict()

    @staticmethod
    def get_available(
        check_in: int,
        check_out: int,
        guests_num: int,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Возвращает доступные номера на даты."""
        rooms = get_available_rooms(
            check_in=check_in,
            check_out=check_out,
            guests_num=guests_num,
        )
        return {"rooms": [room.to_dict() for room in rooms]}


class BookingService:
    """Бизнес-логика для бронирований."""

    @staticmethod
    def book_room(
        room_id: int,
        check_in: int,
        check_out: int,
        first_name: str,
        last_name: str,
    ) -> Dict[str, Any]:
        """
        Создаёт бронирование.

        Возвращает данные бронирования.
        """
        booking = create_booking(
            room_id=room_id,
            check_in=check_in,
            check_out=check_out,
            first_name=first_name,
            last_name=last_name,
        )
        return booking.to_dict()

    @staticmethod
    def is_available(
        room_id: int,
        check_in: int,
        check_out: int,
    ) -> bool:
        """Проверяет, доступен ли номер на даты."""
        return not is_room_booked(
            room_id=room_id,
            check_in=check_in,
            check_out=check_out,
        )

