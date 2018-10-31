import tensorflow as tf

def make_estimator(estimator_class, estimator_args):
    estimator = estimator_class(**estimator_args)

    return estimator
