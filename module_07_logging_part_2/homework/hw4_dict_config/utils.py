import logging
from operator import sub, mul, truediv, add
from typing import Union, Callable

logger = logging.getLogger('utils')  # или logging.getLogger(__name__)


OPERATORS = {
    '+': add,
    '-': sub,
    '*': mul,
    '/': truediv,
}

Numeric = Union[int, float]


def string_to_operator(value: str) -> Callable[[Numeric, Numeric], Numeric]:
    if not isinstance(value, str):
        logger.error("Wrong operator type: %r", value)
        raise ValueError("wrong operator type")

    if value not in OPERATORS:
        logger.error("Wrong operator value: %r", value)
        raise ValueError("wrong operator value")

    logger.debug("Operator %r resolved to function %r", value, OPERATORS[value])
    return OPERATORS[value]