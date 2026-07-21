import logging
from dict_config import configure_logging  # имя файла с dict-конфигом

configure_logging()
logger = logging.getLogger('appLogger')

logger.debug('debug message')
logger.info('info message')
logger.warning('warning message')
logger.error('error message')