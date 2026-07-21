import logging
import sys


class LevelFileHandler(logging.Handler):
    """
    Обработчик, который пишет сообщения разных уровней в разные файлы:
    DEBUG    -> calc_debug.log
    INFO     -> calc_info.log
    WARNING  -> calc_warning.log
    ERROR    -> calc_error.log
    CRITICAL -> calc_critical.log
    """

    def __init__(self):
        super().__init__()
        self.files = {
            logging.DEBUG: open('calc_debug.log', 'a', encoding='utf-8'),
            logging.INFO: open('calc_info.log', 'a', encoding='utf-8'),
            logging.WARNING: open('calc_warning.log', 'a', encoding='utf-8'),
            logging.ERROR: open('calc_error.log', 'a', encoding='utf-8'),
            logging.CRITICAL: open('calc_critical.log', 'a', encoding='utf-8'),
        }

    def emit(self, record: logging.LogRecord) -> None:
        """
        Получает LogRecord и пишет его в файл, соответствующий уровню.
        """
        try:
            msg = self.format(record)  # форматирование через Formatter[web:492][web:508]

            file = self.files.get(record.levelno)
            if file is None:
                # На всякий случай — если уровень нестандартный
                file = self.files[logging.DEBUG]

            file.write(msg + '\n')
            file.flush()
        except Exception:
            # Стандартный способ обработать ошибку внутри handler[web:502][web:508]
            self.handleError(record)

    def close(self) -> None:
        for file in self.files.values():
            try:
                file.close()
            except Exception:
                pass
        super().close()


def get_logger(name):
    """
    Вернуть логгер с:
    - выводом в stdout;
    - файловым обработчиком по уровням;
    - общим форматтером.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # пропускаем все уровни[web:508]

    # Чтобы не плодить обработчики при многократных вызовах get_logger
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt='%(levelname)s | %(name)s | %(asctime)s | %(lineno)d | %(message)s'
    )

    # Обработчик для stdout (StreamHandler на sys.stdout)[web:504]
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    # Наш многоуровневый файловый обработчик
    level_file_handler = LevelFileHandler()
    level_file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(level_file_handler)

    return logger

