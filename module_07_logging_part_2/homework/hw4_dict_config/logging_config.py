import logging
import logging.config
import sys

from level_file_handler import LevelFileHandler  # где у тебя класс обработчика


LOGGING_DICT_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default': {
            'format': '%(levelname)s | %(name)s | %(asctime)s | %(lineno)d | %(message)s',
        },
    },

    'handlers': {
        # Обработчик для stdout
        'stdout': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'stream': sys.stdout,  # обратим внимание: можно передать sys.stdout напрямую[web:520][web:522]
        },

        # Кастомный многоуровневый файловый обработчик
        'level_file': {
            'class': 'level_file_handler.LevelFileHandler',  # модуль.Класс[web:523]
            'level': 'DEBUG',
            'formatter': 'default',
        },
    },

    'loggers': {
        # Логгер для твоего приложения (app.py)
        'app': {
            'handlers': ['stdout', 'level_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Логгер для utils.py
        'utils': {
            'handlers': ['stdout', 'level_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },

    # Корневой логгер, если хочешь, чтобы все безымянные тоже попадали в эти обработчики
    'root': {
        'handlers': ['stdout', 'level_file'],
        'level': 'DEBUG',
    },
}


def configure_logging() -> None:
    """Применить dict-конфигурацию логирования."""
    logging.config.dictConfig(LOGGING_DICT_CONFIG)  # применение словаря[web:520][web:521][web:526][web:528]