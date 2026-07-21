import logging
import sys
from utils import string_to_operator

# Модульный логгер для app
logger = logging.getLogger(__name__)


def calc(args):
    """
    Простейший консольный калькулятор для двух чисел.

    :param args: последовательность из трех элементов: num_1, operator, num_2.
    """
    logger.info("Arguments: %r", args)

    num_1 = args[0]
    operator = args[1]
    num_2 = args[2]

    try:
        num_1 = float(num_1)
        logger.debug("Parsed num_1: %r", num_1)
    except ValueError:
        logger.error("Error while converting number 1: %r", num_1, exc_info=True)
        return

    try:
        num_2 = float(num_2)
        logger.debug("Parsed num_2: %r", num_2)
    except ValueError:
        logger.error("Error while converting number 2: %r", num_2, exc_info=True)
        return

    try:
        operator_func = string_to_operator(operator)
    except ValueError:
        logger.error("Error while resolving operator: %r", operator, exc_info=True)
        return

    result = operator_func(num_1, num_2)

    logger.info("Result: %s", result)
    logger.info("%s %s %s = %s", num_1, operator, num_2, result)


if __name__ == '__main__':
    # Базовая настройка логирования для консольного приложения.
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] %(name)s %(levelname)s: %(message)s',
    )
    import logging
    # calc(sys.argv[1:])
    calc('2+5')

