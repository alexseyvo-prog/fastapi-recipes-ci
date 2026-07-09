"""
Реализуйте контекстный менеджер, который будет игнорировать переданные типы исключений,
возникающие внутри блока with.
Если выбрасывается неожидаемый тип исключения, то он прокидывается выше.
"""

from typing import Collection, Type, Literal, Iterable
from types import TracebackType


class BlockErrors:
    """
    Контекстный менеджер, подавляющий указанные типы исключений.

    Пример:
        err_types = {ZeroDivisionError, TypeError}
        with BlockErrors(err_types):
            1 / 0   # ZeroDivisionError будет проигнорирован

    Логика:
    - В __init__ передаётся коллекция классов-исключений (Type[BaseException]).
    - В __exit__:
        * если исключения не было (exc_type is None) — ничего не подавляем;
        * если exc_type является подклассом одного из переданных типов
          (issubclass(exc_type, ...)) — возвращаем True, исключение подавляется;
        * иначе возвращаем None, исключение прокидывается выше.
    """

    def __init__(self, errors: Collection[Type[BaseException]]) -> None:
        """
        :param errors: коллекция типов исключений, которые нужно игнорировать.
        """
        # Приводим к кортежу, чтобы удобно использовать в issubclass
        if not isinstance(errors, Iterable):
            raise TypeError("errors must be a collection of exception types")
        self._errors = tuple(errors)

    def __enter__(self) -> None:
        # Ничего не предоставляем наружу, просто возвращаем self или None.
        return None

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None
    ) -> Literal[True] | None:
        """
        Вызывается при выходе из блока with.

        :param exc_type: тип возникшего исключения или None
        :param exc_val: объект исключения или None
        :param exc_tb: traceback или None
        :return: True, если исключение нужно подавить; None — если прокинуть выше.
        """
        # Если исключения не было — ничего не подавляем, пусть выполнение продолжается как обычно.
        if exc_type is None:
            return None

        # Если тип возникшего исключения является подклассом одного из заданных типов,
        # подавляем его, вернув True.
        # issubclass умеет принимать кортеж классов вторым аргументом.
        if issubclass(exc_type, self._errors):
            return True

        # Для всех остальных исключений ничего не делаем — они будут прокинуты выше.
        return None