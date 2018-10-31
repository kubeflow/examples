from tensorflow.contrib.factorization import KMeansClustering

import argparse
import inspect
import os
import yaml
from utils import get_args

# TODO: implement appropriate functions for each generated component.
from model import make_estimator
from input_fn import make_input_fn
from train import train


def main(args):
    # turn args into a dict so we can pop the arguments.
    args = vars(args)

    # create estimator
    estimator_args = get_args(args, KMeansClustering.__init__)
    estimator = make_estimator(KMeansClustering, estimator_args)

    # create input_fn
    make_input_fn_args = get_args(args, make_input_fn)
    input_fn = make_input_fn(**make_input_fn_args)

    # train, pass the remaining args
    train(estimator, input_fn, **args)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--npy_uri', default='gs://sandboxdata/cmle-pipelines/X.npy', type=str)
    parser.add_argument('--num_iterations', default=10, type=int)
    parser.add_argument('--num_clusters', default=5, type=int)
    parser.add_argument('--use_mini_batch', default=False, type=bool)
    parser.add_argument('--model_dir', default=None)
    parser.add_argument('--initial_clusters', default='random', type=str)
    parser.add_argument('--distance_metric', default='squared_euclidean', type=str)
    parser.add_argument('--random_seed', default=0, type=int)
    parser.add_argument('--mini_batch_steps_per_iteration', default=1, type=int)
    parser.add_argument('--kmeans_plus_plus_num_retries', default=2, type=int)
    parser.add_argument('--relative_tolerance', default=None)
    parser.add_argument('--config', default=None)
    parser.add_argument('--feature_columns', default=None)

    args, _ = parser.parse_known_args()

    main(args)
