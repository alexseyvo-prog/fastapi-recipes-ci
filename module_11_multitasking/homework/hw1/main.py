"""
Задача об обедающих философах.

Пять философов по очереди размышляют и едят.
Для еды философу нужны две вилки: левая и правая.

Вилки представлены объектами threading.Lock.
Для захвата и освобождения вилок используется
контекстный менеджер with.
"""


import logging
import random
import threading
import time
from typing import List


# Настраиваем вывод информационных сообщений в консоль.
logging.basicConfig(level="INFO")

# Создаём объект логгера для записи событий программы.
logger: logging.Logger = logging.getLogger(__name__)


class Philosopher(threading.Thread):
    """
    Поток, моделирующий поведение одного философа.

    Каждый философ может:
    - размышлять;
    - испытывать голод;
    - захватывать две вилки;
    - есть;
    - снова переходить к размышлениям.
    """

    # Общий флаг работы для всех философов.
    # Когда значение станет False, потоки завершат работу.
    running: bool = True

    def __init__(
        self,
        left_fork: threading.Lock,
        right_fork: threading.Lock,
    ) -> None:
        """
        Инициализирует философа.

        Args:
            left_fork: Вилка, расположенная слева от философа.
            right_fork: Вилка, расположенная справа от философа.
        """
        # Вызываем конструктор родительского класса Thread.
        super().__init__()

        # Сохраняем левую и правую вилки философа.
        self.left_fork: threading.Lock = left_fork
        self.right_fork: threading.Lock = right_fork

        # Чтобы избежать взаимной блокировки, все философы
        # захватывают вилки в одинаковом порядке.
        #
        # Например, сначала берётся вилка с меньшим id,
        # затем вилка с большим id.
        if id(left_fork) < id(right_fork):
            self.first_fork: threading.Lock = left_fork
            self.second_fork: threading.Lock = right_fork
        else:
            self.first_fork = right_fork
            self.second_fork = left_fork

    def run(self) -> None:
        """
        Запускает основной цикл работы философа.

        Метод run автоматически вызывается после philosopher.start().
        Философ последовательно размышляет, голодает и ест.
        """
        # Философ работает, пока общий флаг имеет значение True.
        while self.running:
            # Философ начинает размышлять.
            logger.info(
                f"Philosopher {self.name} starts thinking."
            )

            # Имитируем процесс размышления.
            time.sleep(random.randint(1, 10))

            # Философ проголодался.
            logger.info(
                f"Philosopher {self.name} is hungry."
            )

            # Контекстный менеджер автоматически захватывает
            # первую вилку при входе в блок.
            with self.first_fork:
                logger.info(
                    f"Philosopher {self.name} acquired "
                    f"the first fork."
                )

                # Контекстный менеджер автоматически захватывает
                # вторую вилку при входе во вложенный блок.
                with self.second_fork:
                    logger.info(
                        f"Philosopher {self.name} acquired "
                        f"the second fork."
                    )

                    # Философ ест, удерживая обе вилки.
                    self.dining()

                # При выходе из этого блока вторая вилка
                # автоматически освобождается.

            # При выходе из внешнего блока первая вилка
            # автоматически освобождается.

    def dining(self) -> None:
        """
        Имитирует процесс еды философа.

        Пока выполняется этот метод, философ удерживает
        обе захваченные вилки.
        """
        # Философ начинает есть.
        logger.info(
            f"Philosopher {self.name} starts eating."
        )

        # Имитируем продолжительность еды.
        time.sleep(random.randint(1, 10))

        # Философ закончил есть и возвращается к размышлениям.
        logger.info(
            f"Philosopher {self.name} finishes eating "
            f"and leaves to think."
        )


def main() -> None:
    """
    Создаёт вилки и философов, а затем запускает программу.

    За круглым столом сидят пять философов.
    Между каждой парой соседних философов находится одна вилка.
    """
    # Создаём пять блокировок.
    # Каждая блокировка представляет одну вилку.
    forks: List[threading.Lock] = [
        threading.Lock()
        for _ in range(5)
    ]

    # Создаём пять философов.
    #
    # Для философа с индексом i:
    # - левая вилка имеет индекс i;
    # - правая вилка имеет индекс (i + 1) % 5.
    #
    # Оператор % возвращает к первой вилке после последней.
    philosophers: List[Philosopher] = [
        Philosopher(
            left_fork=forks[i % 5],
            right_fork=forks[(i + 1) % 5],
        )
        for i in range(5)
    ]

    # Разрешаем философам начать работу.
    Philosopher.running = True

    # Запускаем каждый поток-философ.
    for philosopher in philosophers:
        philosopher.start()

    # Оставляем программу работать 200 секунд.
    time.sleep(200)

    # После завершения этого времени запрещаем философам
    # начинать новые циклы размышления и еды.
    Philosopher.running = False

    logger.info("Now we're finishing.")

    # Ожидаем завершения всех потоков.
    # Метод join не позволяет главному потоку завершиться
    # раньше потоков философов.
    for philosopher in philosophers:
        philosopher.join()

    logger.info("All philosophers have finished.")


# Запускаем main только при непосредственном запуске файла.
# При импорте этого модуля функция main автоматически
# выполняться не будет.
if __name__ == "__main__":
    main()