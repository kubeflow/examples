This directory contains data to be used by the unittests.


## Training data

github_function_docstring-train-00000-of-001000

This file was produced by running the Dataflow jobs to preprocess the data
and then just taking one of the shards

TODO(jlewi): Do we also need to run t2t-datagen

## Inference Data

./test_data/export

This is an exported model suitable for training. It can be reproduced by
running the training unittest which will export the model to a temporary
directory. You can then just copy it into the test_data folder.