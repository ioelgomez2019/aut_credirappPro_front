"""Standard-library logger access."""

import logging


def getLogger(name: str) -> logging.Logger:
    return logging.getLogger(name)
