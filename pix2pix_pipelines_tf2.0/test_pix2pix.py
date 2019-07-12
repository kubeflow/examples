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


def test_pix2pix(dataset:str, output:str, model:str)-> str:
    """
    Use the Pix2Pix trained model to generate ("translate") 
    images from the Test dataset
    
    Args:
        dataset     (string) : Full path name to the test dataset (TFRecords file)
        output      (string) : Full path name to the Output ("translated") images
        model       (string) : Full path name to the Pix2Pix model checkpoint
        
    Returns:
        output_path (string) : Path to generated/translated images
    """
    
    # Fake outputs
    output="/mnt/nfs/data/pix2pix_outputs/"
    print(output)

        
    # Output of the Kubeflow Pipeline Component
    with open('/output.txt', 'w') as f:
        f.write(output)

    return output
    

    
    
# ---------
#   Main
# ---------

flags.DEFINE_string('dataset', None, 'Full path name to the test dataset (TFRecords file)')
flags.DEFINE_string('output', None, 'Pull path name to the Output ("translated") images')
flags.DEFINE_string('model', None,  'Full path name to the Pix2Pix model checkpoint')

FLAGS = flags.FLAGS


def main(argv):
    del argv  # Unused.
    
    test_pix2pix(FLAGS.dataset,FLAGS.output, FLAGS.model)


if __name__ == '__main__':
    app.run(main)



    
    

    


    
    