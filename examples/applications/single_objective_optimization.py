import numpy as np
from opytimark.markers.n_dimensional import Sphere

from opytimizer import Opytimizer
from opytimizer.core import Function
from opytimizer.optimizers.swarm import FA, PSO
from opytimizer.spaces import SearchSpace
from opytimizer.utils.callback import CheckpointCallback

# Random seed for experimental consistency
np.random.seed(0)

# Number of agents and decision variables
n_agents = 20
n_variables = 2

# Lower and upper bounds (has to be the same size as `n_variables`)
lower_bound = [-10, -10]
upper_bound = [10, 10]

# Creates the space, optimizer and function
space = SearchSpace(n_agents, n_variables, lower_bound, upper_bound)
optimizer = PSO()
function = Function(Sphere())

# Bundles every piece into Opytimizer class
opt = Opytimizer(space, optimizer, function, store_only_best_agent=True)

# Runs the optimization task
# opt.start(n_iterations=1000)
opt.start(n_iterations=100, callbacks=[CheckpointCallback(frequency=10)])
opt.start(n_iterations=100, callbacks=[CheckpointCallback(frequency=50)])

# opt.save('out.pkl')