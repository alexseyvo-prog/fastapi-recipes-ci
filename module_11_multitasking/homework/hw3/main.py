import logging
import random
import threading
import time
from typing import List


# Изначальное количество доступных билетов.
TOTAL_TICKETS: int = 10

# Общее количество посадочных мест.
TOTAL_SEATS: int = 50

# Количество уже проданных билетов.
SOLD_TICKETS: int = 0

# Количество продавцов и касс.
SELLERS_COUNT: int = 3

# Максимальное количество билетов,
# которое директор печатает за один раз.
PRINT_BATCH: int = 6


logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)


class Seller(threading.Thread):
    """
    Продавец билетов.

    Продавец может продать билет только тогда,
    когда доступен хотя бы один билет.
    """

    def __init__(self, semaphore: threading.Semaphore) -> None:
        """
        Инициализирует продавца.

        Args:
            semaphore: Общий семафор для продавцов и директора.
        """
        super().__init__()

        self.sem: threading.Semaphore = semaphore
        self.tickets_sold: int = 0

        logger.info(
            "Seller %s started work",
            self.name,
        )

    def run(self) -> None:
        """
        Запускает цикл продажи билетов.
        """
        global TOTAL_TICKETS
        global SOLD_TICKETS

        while True:
            self.random_sleep()

            # Продавец и директор используют один семафор.
            with self.sem:
                # Если все места уже проданы,
                # продавец завершает работу.
                if SOLD_TICKETS >= TOTAL_SEATS:
                    break

                # Если билетов временно нет,
                # продавец не завершается.
                # Он продолжит работу после печати новых билетов.
                if TOTAL_TICKETS <= 0:
                    continue

                # Продажа одного билета.
                TOTAL_TICKETS -= 1
                SOLD_TICKETS += 1
                self.tickets_sold += 1

                logger.info(
                    "%s sold one ticket; "
                    "%s tickets available; "
                    "%s tickets sold",
                    self.name,
                    TOTAL_TICKETS,
                    SOLD_TICKETS,
                )

        logger.info(
            "Seller %s sold %s tickets",
            self.name,
            self.tickets_sold,
        )

    @staticmethod
    def random_sleep() -> None:
        """
        Имитирует время обслуживания покупателя.
        """
        time.sleep(random.randint(0, 1))


class Director(threading.Thread):
    """
    Главный директор с печатным станком.

    Когда доступных билетов становится мало,
    директор печатает новую партию билетов.
    Общее количество проданных билетов не может
    превысить количество посадочных мест.
    """

    def __init__(self, semaphore: threading.Semaphore) -> None:
        """
        Инициализирует директора.

        Args:
            semaphore: Общий семафор для синхронизации.
        """
        super().__init__()

        self.sem: threading.Semaphore = semaphore

        logger.info("Director started work")

    def run(self) -> None:
        """
        Запускает цикл проверки количества билетов.
        """
        global TOTAL_TICKETS
        global SOLD_TICKETS

        while True:
            time.sleep(0.2)

            # Пока директор печатает билеты,
            # продавцы не могут изменять TOTAL_TICKETS.
            with self.sem:
                # Если все посадочные места уже заняты,
                # директор завершает работу.
                if SOLD_TICKETS >= TOTAL_SEATS:
                    break

                # Порог равен количеству продавцов.
                # Если осталось не больше трёх билетов,
                # директор пополняет запас.
                if TOTAL_TICKETS <= SELLERS_COUNT:
                    available_places = (
                        TOTAL_SEATS
                        - SOLD_TICKETS
                        - TOTAL_TICKETS
                    )

                    # Нельзя напечатать больше билетов,
                    # чем осталось посадочных мест.
                    tickets_to_print = min(
                        PRINT_BATCH,
                        available_places,
                    )

                    if tickets_to_print > 0:
                        TOTAL_TICKETS += tickets_to_print

                        logger.info(
                            "Director printed %s tickets; "
                            "%s tickets available; "
                            "%s places remain",
                            tickets_to_print,
                            TOTAL_TICKETS,
                            available_places - tickets_to_print,
                        )

        logger.info("Director finished work")


def main() -> None:
    """
    Создаёт общий семафор, продавцов и директора,
    а затем запускает все потоки.
    """
    # Семафор с одним разрешением используется
    # как взаимная блокировка.
    semaphore = threading.Semaphore(1)

    sellers: List[Seller] = [
        Seller(semaphore)
        for _ in range(SELLERS_COUNT)
    ]

    director = Director(semaphore)

    # Сначала запускаем директора.
    director.start()

    # Затем запускаем продавцов.
    for seller in sellers:
        seller.start()

    # Ожидаем завершения продавцов.
    for seller in sellers:
        seller.join()

    # Ожидаем завершения директора.
    director.join()

    logger.info(
        "All places sold: %s",
        SOLD_TICKETS,
    )

    logger.info(
        "Tickets left: %s",
        TOTAL_TICKETS,
    )


if __name__ == "__main__":
    main()