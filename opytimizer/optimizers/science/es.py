"""Electro-Search.
"""

import copy

import numpy as np
from tqdm import tqdm

import opytimizer.math.random as r
import opytimizer.utils.constants as c
import opytimizer.utils.exception as e
import opytimizer.utils.history as h
import opytimizer.utils.logging as l
from opytimizer.core.optimizer import Optimizer

logger = l.get_logger(__name__)


class ES(Optimizer):
    """An ES class, inherited from Optimizer.

    This is the designed class to define ES-related
    variables and methods.

    References:
        A. Tabari, A. Ahmad. A new optimization method: Electro-Search algorithm.
        Computers & Chemical Engineering (2017).

    """

    def __init__(self, algorithm='ES', hyperparams=None):
        """Initialization method.

        Args:
            algorithm (str): Indicates the algorithm name.
            hyperparams (dict): Contains key-value parameters to the meta-heuristics.

        """

        logger.info('Overriding class: Optimizer -> ES.')

        # Override its parent class with the receiving hyperparams
        super(ES, self).__init__(algorithm)

        # Now, we need to build this class up
        self._build(hyperparams)

        logger.info('Class overrided.')
