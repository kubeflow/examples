This directory contains data to be used by the unittests.


## Training data

kf_github_function_docstring-train-00000-of-001000

This file was produced by running the test similarity_transform_test.
The test calls *t2t_trainer.generate_data()* which is a null op if the data
exists but will otherwise generate the model.

## Inference Data

./test_data/export

This is an exported model suitable for training. It can be reproduced by
running the training unittest which will export the model to a temporary
directory. You can then just copy it into the test_data folder.