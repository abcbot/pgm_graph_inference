"""

Interface for inference algorithms
Authors: kkorovin@cs.cmu.edu

"""

from inference.bp import BeliefPropagation
from inference.gnn_inference import GatedGNNInference
from inference.exact import ExactInference
from inference.mcmc import GibbsSampling


def get_algorithm(algo_name):
    """ Returns a constructor """
    if algo_name == "bp":
        return BeliefPropagation
    elif algo_name == "gnn_inference":
        return GatedGNNInference
    elif algo_name == "exact":
        return ExactInference
    elif algo_name == "mcmc":
        return GibbsSampling
    else:
        raise ValueError("Inference algorithm {} not supported".format(algo_name))