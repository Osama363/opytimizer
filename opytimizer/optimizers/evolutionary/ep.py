"""Evolutionary Programming.
"""

import copy

import numpy as np
from tqdm import tqdm

import opytimizer.math.random as r
import opytimizer.utils.exception as e
import opytimizer.utils.history as h
import opytimizer.utils.logging as l
from opytimizer.core.optimizer import Optimizer

logger = l.get_logger(__name__)


class EP(Optimizer):
    """An EP class, inherited from Optimizer.

    This is the designed class to define EP-related
    variables and methods.

    References:
        A. E. Eiben and J. E. Smith. Introduction to Evolutionary Computing.
        Natural Computing Series (2013).

    """

    def __init__(self, params=None):
        """Initialization method.

        Args:
            params (dict): Contains key-value parameters to the meta-heuristics.

        """

        # Overrides its parent class with the receiving params
        super(EP, self).__init__()

        # Size of bout during the tournament selection
        self.bout_size = 0.1

        # Clipping ratio to helps the algorithm's convergence
        self.clip_ratio = 0.05

        # Builds the class
        self.build(params)

        logger.info('Class overrided.')

    @property
    def bout_size(self):
        """float: Size of bout during the tournament selection.

        """

        return self._bout_size

    @bout_size.setter
    def bout_size(self, bout_size):
        if not isinstance(bout_size, (float, int)):
            raise e.TypeError('`bout_size` should be a float or integer')
        if bout_size < 0 or bout_size > 1:
            raise e.ValueError('`bout_size` should be between 0 and 1')

        self._bout_size = bout_size

    @property
    def clip_ratio(self):
        """float: Clipping ratio to helps the algorithm's convergence.

        """

        return self._clip_ratio

    @clip_ratio.setter
    def clip_ratio(self, clip_ratio):
        if not isinstance(clip_ratio, (float, int)):
            raise e.TypeError('`clip_ratio` should be a float or integer')
        if clip_ratio < 0 or clip_ratio > 1:
            raise e.ValueError('`clip_ratio` should be between 0 and 1')

        self._clip_ratio = clip_ratio

    def _mutate_parent(self, agent, function, strategy):
        """Mutates a parent into a new child (eq. 5.1).

        Args:
            agent (Agent): An agent instance to be reproduced.
            function (Function): A Function object that will be used as the objective function.
            strategy (np.array): An array holding the strategies that conduct the searching process.

        Returns:
            A mutated child.

        """

        # Makes a deepcopy on selected agent
        a = copy.deepcopy(agent)

        # Generates a uniform random number
        r1 = r.generate_gaussian_random_number()

        # Updates its position
        a.position += strategy * r1

        # Clips its limits
        a.clip_by_bound()

        # Calculates its fitness
        a.fit = function(a.position)

        return a

    def _update_strategy(self, strategy, lower_bound, upper_bound):
        """Updates the strategy and performs a clipping process to help its convergence (eq. 5.2).

        Args:
            strategy (np.array): An strategy array to be updated.
            lower_bound (np.array): An array holding the lower bounds.
            upper_bound (np.array): An array holding the upper bounds.

        Returns:
            The updated strategy.

        """

        # Calculates the number of variables and dimensions
        n_variables, n_dimensions = strategy.shape[0], strategy.shape[1]

        # Generates a uniform random number
        r1 = r.generate_gaussian_random_number(size=(n_variables, n_dimensions))

        # Calculates the new strategy
        new_strategy = strategy + r1 * (np.sqrt(np.abs(strategy)))

        # For every decision variable
        for j, (lb, ub) in enumerate(zip(lower_bound, upper_bound)):
            # Uses the clip ratio to help the convergence
            new_strategy[j] = np.clip(new_strategy[j], lb, ub) * self.clip_ratio

        return new_strategy

    def update(self, agents, n_agents, function, strategy):
        """Wraps evolution over all agents and variables.

        Args:
            agents (list): List of agents.
            n_agents (int): Number of possible agents in the space.
            function (Function): A Function object that will be used as the objective function.
            strategy (np.array): An array of strategies.

        Returns:
            A new population with more fitted individuals.

        """

        # Creating a list for the produced children
        children = []

        # Iterates through all agents
        for i, agent in enumerate(agents):
            # Mutates a parent and generates a new child
            a = self._mutate_parent(agent, function, strategy[i])

            # Updates the strategy
            strategy[i] = self._update_strategy(strategy[i], agent.lb, agent.ub)

            # Appends the mutated agent to the children
            children.append(a)

        # Joins both populations
        agents += children

        # Number of individuals to be selected
        n_individuals = int(n_agents * self.bout_size)

        # Creates an empty array of wins
        wins = np.zeros(len(agents))

        # Iterates through all agents in the new population
        for i, agent in enumerate(agents):
            # Iterate through all tournament individuals
            for _ in range(n_individuals):
                # Gathers a random index
                index = r.generate_integer_random_number(0, len(agents))

                # If current agent's fitness is smaller than selected one
                if agent.fit < agents[index].fit:
                    # Increases its winning by one
                    wins[i] += 1

        # Sorts the agents list based on its winnings
        agents = [agents for _, agents in sorted(
            zip(wins, agents), key=lambda pair: pair[0], reverse=True)]

        return agents[:n_agents]

    def run(self, space, function, store_best_only=False, pre_evaluate=None):
        """Runs the optimization pipeline.

        Args:
            space (Space): A Space object that will be evaluated.
            function (Function): A Function object that will be used as the objective function.
            store_best_only (bool): If True, only the best agent of each iteration is stored in History.
            pre_evaluate (callable): This function is executed before evaluating the function being optimized.

        Returns:
            A History object holding all agents' positions and fitness achieved during the task.

        """

        # Instantiate an array of strategies
        strategy = np.zeros((space.n_agents, space.n_variables, space.n_dimensions))

        # Iterates through all agents
        for i in range(space.n_agents):
            # For every decision variable
            for j, (lb, ub) in enumerate(zip(space.lb, space.ub)):
                # Initializes the strategy array with the proposed EP distance
                strategy[i][j] = 0.05 * r.generate_uniform_random_number(
                    0, ub - lb, size=space.agents[i].n_dimensions)

        # Initial search space evaluation
        self._evaluate(space, function, hook=pre_evaluate)

        # We will define a History object for further dumping
        history = h.History(store_best_only)

        # Initializing a progress bar
        with tqdm(total=space.n_iterations) as b:
            # These are the number of iterations to converge
            for t in range(space.n_iterations):
                logger.to_file(f'Iteration {t+1}/{space.n_iterations}')

                # Updates agents
                space.agents = self._update(space.agents, space.n_agents, function, strategy)

                # Checking if agents meet the bounds limits
                space.clip_by_bound()

                # After the update, we need to re-evaluate the search space
                self._evaluate(space, function, hook=pre_evaluate)

                # Every iteration, we need to dump agents and best agent
                history.dump(agents=space.agents, best_agent=space.best_agent)

                # Updates the `tqdm` status
                b.set_postfix(fitness=space.best_agent.fit)
                b.update()

                logger.to_file(f'Fitness: {space.best_agent.fit}')
                logger.to_file(f'Position: {space.best_agent.position}')

        return history
