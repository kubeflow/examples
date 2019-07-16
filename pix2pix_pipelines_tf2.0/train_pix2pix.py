from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf
import os
import json
import time

from utils import *

from absl import app
from absl import flags
from absl import logging


# -------------------------------------
#   Kubeflow Pipeline Component code
# -------------------------------------


def train_pix2pix(pathdataset:str, pathmodel:str, pathlogs:str, epochs:int=200)-> str:
    """
    Train Pix2Pix. 
    
    Args:
        pathdataset      (string) : Full path name to the training dataset (TFRecords file)
        pathmodel        (string) : Full path name to the Pix2Pix model checkpoint
        pathlogs         (string) : Full path name to the Tensorboard logs directory
        epochs           (int)    : Number of training epochs
        
    Returns:
        model            (string) : Full path name to the Pix2Pix model checkpoint
    """
    
    
    # Enable Kubeflow Pipelines UI built-in support for Tensorboard
    try:
        metadata = {
            'outputs' : [{
                'type': 'tensorboard',
                'source': pathlogs,
            }]
        }

        # This works only inside Docker containers
        with open('/mlpipeline-ui-metadata.json', 'w') as f:
            json.dump(metadata, f)

    except PermissionError:
        pass

    
    # Training loop
    for e in range(1):
    
        # Open (and shuffle) the dataset
        dataset = get_dataset(pathdataset)

        steps = 0
        
        # Iterate over the dataset
        for example in dataset:

            # Extract the training pictures pair
            img_a, img_b = decode_tfrecords_example(example)

            # Perform Data augmentation
            img_a, img_b = transform_image(img_a, img_b, initial_resize=286, crop_resize=256)

            # WIP : display 10training set examples
            display_img(img_a, img_b, normalized=True)
            steps+=1
            if steps > 9:
                break
    

    # Fake outputs
    model="/mnt/nfs/data/models/facades.checkpoints"
    print(model)

    
    # Output of the Kubeflow Pipeline Component
    try:
        metadata = {
            'outputs' : [{
                'type': 'tensorboard',
                'source': pathlogs,
            }]
        }

        # This works only inside Docker containers
        with open('/output.txt', 'w') as f:
            f.write(model)

    except PermissionError:
        pass
    
    return model
    

    


    
# ---------
#   Main
# ---------

flags.DEFINE_string('pathdataset', None, 'Full path name to the training dataset (TFRecords file)')
flags.DEFINE_string('pathmodel', None, 'Full path name to the Pix2Pix model checkpoint')
flags.DEFINE_string('pathlogs', None, 'Full path name to the Tensorboard log directory')
flags.DEFINE_integer('epochs', 200, 'Number of training epochs')

FLAGS = flags.FLAGS


def main(argv):
    del argv  # Unused.
    
    train_pix2pix(FLAGS.pathdataset, FLAGS.pathmodel, FLAGS.pathlogs, FLAGS.epochs)


if __name__ == '__main__':
    app.run(main)



    
    

    


    
    