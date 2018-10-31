import tensorflow as tf

def train(kmeans, input_fn, **kwargs):
    num_iterations = kwargs['num_iterations']

    previous_centers = None
    for _ in xrange(num_iterations):
        kmeans.train(input_fn)
        cluster_centers = kmeans.cluster_centers()

        if previous_centers is not None:
            print 'delta:', cluster_centers - previous_centers

        previous_centers = cluster_centers
        print 'score:', kmeans.score(input_fn)

    print 'cluster centers:', cluster_centers
