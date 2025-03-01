class ZephyrException(Exception):
    """Base class for Zephyr exceptions"""


class InvalidAuthError(ZephyrException):
    """Invalid authentication"""
