import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s %(asctime)s %(name)s %(message)s')


class LoggerFactory:
    def __init__(self):
        self.loggers = []

    def get_logger(self, name: str, level: int = logging.DEBUG):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        self.loggers.append(logger)
        return logger

    def set_level(self, level: str):
        for logger in self.loggers:
            logger.setLevel(level)


logger_factory = LoggerFactory()
