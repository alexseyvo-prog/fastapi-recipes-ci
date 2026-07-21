import logging.config

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

        'utils_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'INFO',
            'formatter': 'default',
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
            'stream': 'ext://sys.stdout',
        },

        # Новый обработчик — отправка логов на централизованный сервер[web:586][web:582][web:589]
        'http_logs': {
            'class': 'http_log_handler.JsonHTTPHandler',  # модуль.Класс
            'level': 'INFO',
            'formatter': 'default',
        },
    },

    'loggers': {
        'utils': {
            'handlers': ['utils_file', 'http_logs'],  # пишем в файл и отправляем на сервер
            'level': 'INFO',
            'propagate': False,
        },

        'app': {
            'handlers': ['app_stdout', 'http_logs'],
            'level': 'DEBUG',
            'propagate': False,
        },

        # при желании можно настроить root,
        # но чтобы не получать лишние логи от urllib, лучше оставить его без http_logs[web:587][web:581]
        # 'root': {
        #     'handlers': ['stdout'],
        #     'level': 'WARNING',
        # },
    },
}


def configure_logging() -> None:
    logging.config.dictConfig(LOGGING_DICT_CONFIG)