"""
Иногда возникает необходимость перенаправить вывод в нужное нам место внутри программы по ходу её выполнения.
Реализуйте контекстный менеджер, который принимает два IO-объекта (например, открытые файлы)
и перенаправляет туда стандартные потоки stdout и stderr.

Аргументы контекстного менеджера должны быть непозиционными,
чтобы можно было ещё перенаправить только stdout или только stderr.
"""

import sys
from types import TracebackType
from typing import Type, Literal, IO, Optional


class Redirect:
    """
    Контекстный менеджер для временного перенаправления sys.stdout и sys.stderr.

    Пример:
        stdout_file = open("stdout.txt", "w")
        stderr_file = open("stderr.txt", "w")

        with Redirect(stdout=stdout_file, stderr=stderr_file):
            print("Это уйдёт в stdout.txt")
            raise Exception("Это уйдёт в stderr.txt")

    После выхода из блока with sys.stdout и sys.stderr будут восстановлены.
    """

    def __init__(self, *, stdout: Optional[IO] = None, stderr: Optional[IO] = None) -> None:
        """
        :param stdout: IO-объект (например, файл), куда временно перенаправить sys.stdout.
        :param stderr: IO-объект, куда временно перенаправить sys.stderr.

        Параметры объявлены как именованные (через *), чтобы нельзя было
        передать их позиционно и можно было перенаправлять только один из потоков:
            Redirect(stdout=...)
            Redirect(stderr=...)
        """
        self._new_stdout = stdout
        self._new_stderr = stderr

        self._old_stdout: Optional[IO] = None
        self._old_stderr: Optional[IO] = None

    def __enter__(self) -> "Redirect":
        """
        Сохраняет текущие sys.stdout/sys.stderr и устанавливает новые значения,
        если они переданы в конструктор.
        """
        # Сохраняем старые потоки
        self._old_stdout = sys.stdout
        self._old_stderr = sys.stderr

        # Перенаправляем stdout, если указан новый поток
        if self._new_stdout is not None:
            sys.stdout = self._new_stdout  # type: ignore[assignment]

        # Перенаправляем stderr, если указан новый поток
        if self._new_stderr is not None:
            sys.stderr = self._new_stderr  # type: ignore[assignment]

        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None
    ) -> Literal[True] | None:
        """
        Восстанавливает исходные значения sys.stdout и sys.stderr.

        :param exc_type: тип исключения (если оно возникло внутри with) или None
        :param exc_val: экземпляр исключения или None
        :param exc_tb: traceback или None
        :return: None — исключения не подавляются и прокидываются дальше.
        """
        # Восстанавливаем именно сохранённые значения, чтобы корректно работали вложенные блоки.
        if self._old_stdout is not None:
            sys.stdout = self._old_stdout  # type: ignore[assignment]
        if self._old_stderr is not None:
            sys.stderr = self._old_stderr  # type: ignore[assignment]

        # Исключения не подавляем
        return None