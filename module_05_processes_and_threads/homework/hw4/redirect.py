"""
Иногда возникает необходимость перенаправить вывод в нужное нам место внутри программы по ходу её выполнения.
Реализуйте контекстный менеджер, который принимает два IO-объекта (например, открытые файлы)
и перенаправляет туда стандартные потоки stdout и stderr.

Аргументы контекстного менеджера должны быть непозиционными,
чтобы можно было ещё перенаправить только stdout или только stderr.
"""

import sys
import traceback
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

    После выхода из блока with sys.stdout и sys.stderr будут восстановлены,
    а трейсбек исключения внутри блока будет записан в stderr_file и подавлен.
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
        Если внутри блока with произошло исключение, записывает полный трейсбек
        в текущий sys.stderr (перенаправленный поток) и подавляет исключение.

        :param exc_type: тип исключения (если оно возникло внутри with) или None
        :param exc_val: экземпляр исключения или None
        :param exc_tb: traceback или None
        :return:
            - True  — если было исключение и оно записано в stderr (подавляем его).
            - None  — если исключения не было, ничего не подавляем.
        """
        # Если было исключение, выводим его трейсбек в текущий sys.stderr
        if exc_type is not None:
            # traceback.format_exception возвращает список строк с трейсбеком.[web:443]
            tb_text = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
            # Пишем в текущий sys.stderr (сейчас он указывает на файл/IO, переданный в Redirect)
            sys.stderr.write(tb_text)
            sys.stderr.flush()

        # Восстанавливаем исходные значения потоков (важно для вложенных блоков).[web:440]
        if self._old_stdout is not None:
            sys.stdout = self._old_stdout  # type: ignore[assignment]
        if self._old_stderr is not None:
            sys.stderr = self._old_stderr  # type: ignore[assignment]

        # Если было исключение — мы его уже записали в файл и хотим подавить.
        if exc_type is not None:
            return True

        # Исключения не было — ничего подавлять не нужно.
        return None