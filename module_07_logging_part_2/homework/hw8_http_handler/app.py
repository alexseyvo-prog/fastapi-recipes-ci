import logging
import sys

from utils import string_to_operator
from logging_config import configure_logging  # новая функция из dict-конфигурации


logger = logging.getLogger('app')  # или logging.getLogger(__name__)


def calc(args):
    logger.info("Arguments: %r", args)
    # остальной код калькулятора...


if __name__ == '__main__':
    configure_logging()   # применяем dict-конфиг
    calc('2+3')
    calc('2z3')
    calc('2^3')