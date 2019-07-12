from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import os

from absl import app
from absl import flags
from absl import logging


# -------------------------------------
#   Kubeflow Pipeline Component code
# -------------------------------------


def train_pix2pix(dataset:str, model:str, epochs:int=200)-> str:
    """
    Train Pix2Pix. 
    
    Args:
        dataset      (string) : Full path name to the training dataset (TFRecords file)
        model        (string) : Full path name to the Pix2Pix model checkpoint
        epochs       (int)    : Number of training epochs
        
    Returns:
        model        (string) : Full path name to the Pix2Pix model checkpoint
    """

    # Fake outputs
    model="/mnt/nfs/data/models/facades.checkpoints"
    print(model)

        
    # Output of the Kubeflow Pipeline Component
    with open('/output.txt', 'w') as f:
        f.write(model)

    return model
    

    


    
# ---------
#   Main
# ---------

flags.DEFINE_string('dataset', None, 'Full path name to the training dataset (TFRecords file)')
flags.DEFINE_integer('epochs', 200, 'Number of training epochs')
flags.DEFINE_string('model', None, 'Full path name to the Pix2Pix model checkpoint')

FLAGS = flags.FLAGS


def main(argv):
    del argv  # Unused.
    
    train_pix2pix(FLAGS.dataset, FLAGS.model, FLAGS.epochs)


if __name__ == '__main__':
    app.run(main)



    
    

    


    
    