# TODO переписать реализацию ini-файла в формате dict-конфигурации.
import logging.config

LOGGING_DICT_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'fileFormatter': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'consoleFormatter': {
            'format': '%(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },

    'handlers': {
        'consoleHandler': {
            'class': 'logging.StreamHandler',
            'level': 'WARNING',
            'formatter': 'consoleFormatter',
            'stream': 'ext://sys.stdout',
        },
        'fileHandler': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'fileFormatter',
            'filename': 'logfile.log',
        },
    },

    'loggers': {
        'appLogger': {
            'level': 'DEBUG',
            'handlers': ['consoleHandler', 'fileHandler'],
            'propagate': False,
        },
    },

    'root': {
        'level': 'DEBUG',
        'handlers': ['consoleHandler'],
    },
}


def configure_logging() -> None:
    logging.config.dictConfig(LOGGING_DICT_CONFIG)