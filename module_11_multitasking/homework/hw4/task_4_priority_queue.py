"""
Задача с приоритетной очередью.

Producer создаёт задачи и добавляет их в PriorityQueue.
Consumer извлекает задачи в порядке приоритета
и выполняет их.

Меньшее значение приоритета означает более высокий приоритет:
0 важнее 1, 1 важнее 2 и так далее.
"""


import logging
import random
import threading
import time
from dataclasses import dataclass, field
from itertools import count
from queue import PriorityQueue
from typing import Any, Callable, Dict, Tuple


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class Task:
    """
    Описывает задачу для выполнения.

    Attributes:
        priority: Приоритет задачи.
        function: Функция, которую необходимо выполнить.
        args: Позиционные аргументы функции.
        kwargs: Именованные аргументы функции.
    """

    priority: int
    function: Callable[..., Any] = field(repr=False)
    args: Tuple[Any, ...] = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        """
        Возвращает строковое представление задачи.
        """
        return f"Task(priority={self.priority})"


class Producer(threading.Thread):
    """
    Поток, создающий задачи.

    Producer работает только с очередью и не знает
    о существовании Consumer.
    """

    def __init__(
        self,
        task_queue: PriorityQueue,
    ) -> None:
        """
        Инициализирует Producer.

        Args:
            task_queue: Приоритетная очередь задач.
        """
        super().__init__()

        self.task_queue: PriorityQueue = task_queue

    def run(self) -> None:
        """
        Создаёт десять задач и добавляет их в очередь.
        """
        logger.info("Producer: Running")

        # Счётчик нужен, чтобы задачи с одинаковым приоритетом
        # не сравнивались между собой.
        task_number = count()

        for _ in range(10):
            priority = random.randint(0, 9)
            sleep_time = random.random()

            task = Task(
                priority=priority,
                function=time.sleep,
                args=(sleep_time,),
            )

            # Все элементы очереди имеют одинаковую структуру:
            #
            # (приоритет, порядковый номер, задача)
            #
            # PriorityQueue сначала сравнивает приоритет,
            # а затем порядковый номер.
            self.task_queue.put(
                (
                    task.priority,
                    next(task_number),
                    task,
                )
            )

        # Специальная сигнальная задача.
        #
        # Бесконечный приоритет гарантирует, что Consumer
        # получит её после всех обычных задач.
        self.task_queue.put(
            (
                float("inf"),
                next(task_number),
                None,
            )
        )

        logger.info("Producer: Done")


class Consumer(threading.Thread):
    """
    Поток, выполняющий задачи.

    Consumer получает задачи только из очереди
    и не взаимодействует с Producer напрямую.
    """

    def __init__(
        self,
        task_queue: PriorityQueue,
    ) -> None:
        """
        Инициализирует Consumer.

        Args:
            task_queue: Приоритетная очередь задач.
        """
        super().__init__()

        self.task_queue: PriorityQueue = task_queue

    def run(self) -> None:
        """
        Извлекает задачи из очереди и выполняет их.
        """
        logger.info("Consumer: Running")

        while True:
            # Получаем три элемента:
            # приоритет, порядковый номер и задачу.
            priority, task_number, task = (
                self.task_queue.get()
            )

            # Проверяем сигнальную задачу.
            if task is None:
                self.task_queue.task_done()
                break

            logger.info(
                f">running {task}. "
                f"{task.function.__name__}{task.args}"
            )

            # Выполняем функцию задачи.
            task.function(
                *task.args,
                **task.kwargs,
            )

            # Сообщаем очереди, что задача выполнена.
            self.task_queue.task_done()

        logger.info("Consumer: Done")


def main() -> None:
    """
    Создаёт очередь, Producer и Consumer,
    а затем запускает их.
    """
    # Создаём приоритетную очередь.
    task_queue: PriorityQueue = PriorityQueue()

    # Передаём одну и ту же очередь обоим потокам.
    producer = Producer(task_queue)
    consumer = Consumer(task_queue)

    # Сначала Producer добавляет все задачи.
    producer.start()
    producer.join()

    # После завершения Producer запускаем Consumer.
    consumer.start()

    # Ожидаем выполнения всех задач.
    task_queue.join()

    # Ожидаем завершения Consumer.
    consumer.join()


if __name__ == "__main__":
    main()