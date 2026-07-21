import logging


class LevelFileHandler(logging.Handler):
    """
    Обработчик, который пишет сообщения разных уровней в разные файлы.
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
        msg = self.format(record)
        file = self.files.get(record.levelno, self.files[logging.DEBUG])
        file.write(msg + '\n')
        file.flush()

    def close(self) -> None:
        for file in self.files.values():
            try:
                file.close()
            except Exception:
                pass
        super().close()