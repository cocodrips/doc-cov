"""Full document module."""
from . import package_A
import logging # unused 

class NonPackageFullDoc():
    """
    Short class summary.

    .....
    """

    def __init__(self):
        """init"""
        pass

    def class_doc_func(self):
        """
        Class func
        """
        pass

    def class_no_doc_func(self):
        pass


def non_package_function(arg1, arg2):
    """
    Summary.

    Description

    :param arg1(int): ...
    :param arg2(str): ...
    :return:
        bool: ...
    """
    return True
