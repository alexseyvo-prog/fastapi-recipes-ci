import json
import logging
from logging.handlers import HTTPHandler


class JsonHTTPHandler(HTTPHandler):
    """
    Обработчик, отправляющий LogRecord на лог-сервер в виде JSON через POST.
    """

    def __init__(self, host='127.0.0.1:5000', url='/log', method='POST'):
        super().__init__(host, url, method=method)

    def mapLogRecord(self, record: logging.LogRecord) -> dict:
        """
        Преобразуем LogRecord в словарь для отправки.
        """
        return {
            'name': record.name,
            'level': record.levelname,
            'message': record.getMessage(),
            'time': record.asctime if hasattr(record, 'asctime') else None,
            'pathname': record.pathname,
            'lineno': record.lineno,
        }