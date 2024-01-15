import logging

__all__ = ["get_logger"]

import sys

logging.basicConfig()


def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.propagate = False

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s][%(levelname)s][%(name)s][%(funcName)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ),
    )
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger
