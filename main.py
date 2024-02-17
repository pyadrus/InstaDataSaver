# Новый проект
from loguru import logger  # https://loguru.readthedocs.io/en/stable/overview.html

logger.add("log/log.log")

logger.info('Запуск скрипта')
