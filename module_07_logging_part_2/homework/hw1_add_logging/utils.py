import logging
from typing import Union, Callable
from operator import sub, mul, truediv, add

logger = logging.getLogger(__name__)

OPERATORS = {
    '+': add,
    '-': sub,
    '*': mul,
    '/': truediv,
}

Numeric = Union[int, float]


def string_to_operator(value: str) -> Callable[[Numeric, Numeric], Numeric]:
    """
    Convert string to arithmetic function.
    :param value: basic arithmetic operator as string.
    :raises ValueError: если тип оператора некорректен или оператор не поддерживается.
    """
    if not isinstance(value, str):
        logger.error("Wrong operator type: %r", value)
        raise ValueError("wrong operator type")

    if value not in OPERATORS:
        logger.error("Wrong operator value: %r", value)
        raise ValueError("wrong operator value")

    logger.debug("Operator %r resolved to function %r", value, OPERATORS[value])
    return OPERATORS[value]
