import logging.config
from logging.handlers import TimedRotatingFileHandler
from ascii_filter import AsciiFilter  # чтобы модуль был доступен[web:572]


LOGGING_DICT_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default': {
            'format': '%(levelname)s | %(name)s | %(asctime)s | %(lineno)d | %(message)s',
        },
    },

    'filters': {
        'ascii_only': {
            '()': 'ascii_filter.AsciiFilter',  # модуль.Класс, как для кастомного фильтра[web:572][web:577]
        },
    },

    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filters': ['ascii_only'],   # применяем фильтр к выводу в stdout[web:576][web:580]
            'stream': 'ext://sys.stdout',
        },

        'utils_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'INFO',
            'formatter': 'default',
            'filters': ['ascii_only'],   # и к файлу utils.log
            'filename': 'utils.log',
            'when': 'H',
            'interval': 1,
            'backupCount': 10,
            'encoding': 'utf-8',
            'utc': True,
        },

        'app_stdout': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filters': ['ascii_only'],   # если хочешь фильтровать и app
            'stream': 'ext://sys.stdout',
        },
    },

    'loggers': {
        'utils': {
            'handlers': ['utils_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'app': {
            'handlers': ['app_stdout'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

def configure_logging() -> None:
    logging.config.dictConfig(LOGGING_DICT_CONFIG)