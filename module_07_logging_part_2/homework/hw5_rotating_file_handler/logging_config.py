import logging.config
from logging.handlers import TimedRotatingFileHandler  # только чтобы модуль был доступен[web:504][web:531][web:536]


LOGGING_DICT_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default': {
            'format': '%(levelname)s | %(name)s | %(asctime)s | %(lineno)d | %(message)s',
        },
    },

    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'stream': 'ext://sys.stdout',
        },

        # Обработчик для utils.log с ротацией по времени[web:530][web:531][web:536]
        'utils_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'INFO',
            'formatter': 'default',
            'filename': 'utils.log',
            'when': 'H',        # ротация по часам[web:531][web:536]
            'interval': 1,      # каждые 1 час
            'backupCount': 10,  # храним не более 10 файлов (примерно последние 10 часов)[web:529][web:536]
            'encoding': 'utf-8',
            'utc': True,
        },

        # если нужны другие обработчики для app, можно оставить, но для задачи 5 они не обязательны
        'app_stdout': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'stream': 'ext://sys.stdout',
        },
    },

    'loggers': {
        # логгер utils с отдельным файловым обработчиком и без распространения вверх[web:508][web:528]
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

    # при желании можно настроить root, но для задачи 5 важно, чтобы utils жил отдельно
    # 'root': {
    #     'handlers': ['stdout'],
    #     'level': 'WARNING',
    # },
}


def configure_logging() -> None:
    logging.config.dictConfig(LOGGING_DICT_CONFIG)