from flask import Flask, request, jsonify
from typing import Any, Dict, List

from services import RoomService, BookingService


def register_routes(app: Flask) -> None:
    """Регистрирует endpoint'ы."""

    @app.route('/add-room', methods=['POST'])
    def add_room() -> Any:
        """Добавляет новый номер."""
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        floor = data.get('floor')
        beds = data.get('beds')
        guest_num = data.get('guestNum')
        price = data.get('price')

        if not all([floor, beds, guest_num, price]):
            return jsonify({
                "error": "Fields 'floor', 'beds', 'guestNum', 'price' are required"
            }), 400

        room = RoomService.add_room(
            floor=floor,
            beds=beds,
            guest_num=guest_num,
            price=price,
        )

        return jsonify(room), 200

    @app.route('/room', methods=['GET'])
    def get_room() -> Any:
        check_in = request.args.get('checkIn')
        check_out = request.args.get('checkOut')
        guests_num = request.args.get('guestsNum')

        # Если параметров нет — возвращаем пустой список
        if not check_in or not check_out or not guests_num:
            return jsonify({"rooms": []}), 200

        try:
            check_in_int = int(check_in)
            check_out_int = int(check_out)
            guests_num_int = int(guests_num)
        except ValueError:
            return jsonify({
                "error": "Parameters must be integers"
            }), 400

        if check_in_int >= check_out_int:
            return jsonify({
                "error": "checkIn must be less than checkOut"
            }), 400

        if guests_num_int <= 0:
            return jsonify({
                "error": "guestsNum must be greater than 0"
            }), 400

        result = RoomService.get_available(
            check_in=check_in_int,
            check_out=check_out_int,
            guests_num=guests_num_int,
        )

        return jsonify(result), 200

    @app.route('/booking', methods=['POST'])
    def create_booking() -> Any:
        """Создаёт бронирование."""
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        booking_dates = data.get('bookingDates')
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        room_id = data.get('roomId')

        if not booking_dates:
            return jsonify({
                "error": "Field 'bookingDates' is required"
            }), 400

        check_in = booking_dates.get('checkIn')
        check_out = booking_dates.get('checkOut')

        if not all([check_in, check_out, first_name, last_name, room_id]):
            return jsonify({
                "error": (
                    "Fields 'bookingDates.checkIn', 'bookingDates.checkOut', "
                    "'firstName', 'lastName', 'roomId' are required"
                )
            }), 400

        # Проверяем, доступен ли номер
        if not BookingService.is_available(
                room_id=room_id,
                check_in=check_in,
                check_out=check_out,
        ):
            return jsonify({"error": "Room is already booked for these dates"}), 409

        booking = BookingService.book_room(
            room_id=room_id,
            check_in=check_in,
            check_out=check_out,
            first_name=first_name,
            last_name=last_name,
        )

        return jsonify(booking), 200