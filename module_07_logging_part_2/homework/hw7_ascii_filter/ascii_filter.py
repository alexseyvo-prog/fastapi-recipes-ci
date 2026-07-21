import logging
import string


class AsciiFilter(logging.Filter):
    """
    Фильтр, пропускающий только сообщения, состоящие из ASCII-символов.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()

        # Вариант 1: использовать встроенный str.isascii (Python 3.7+)[web:574][web:578]
        if hasattr(msg, 'isascii'):
            return msg.isascii()

        # Вариант 2: своя реализация через string.printable[web:575]
        printable = set(string.printable)
        return all(ch in printable for ch in msg)