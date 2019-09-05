from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import app
from absl import flags
from absl import logging

from utils import get_dataset, decode_tfrecords_example, normalize, save_image #KFP-NEST-IMPORT
from model import Generator, Discriminator, discriminator_loss, generator_loss   #KFP-NEST-IMPORT

import matplotlib.pyplot as plt ### DEBUG

# -------------------------------------
#   Kubeflow Pipeline Component code
# -------------------------------------
#
#  Note: In order to build a Kubeflow
#  pipeline, we need to specify the
#  input/output types of the python
#  function used to build a Kubeflow
#  pipeline component.
# -------------------------------------
def test_pix2pix(pathdataset:str, pathoutput:str, pathmodel:str)-> str:
    """
    Use the Pix2Pix trained model to generate ("translate")
    images from the Test dataset

    Args:
        pathdataset     (string) : Full path name to the test dataset (TFRecords file)
        pathoutput      (string) : Full path name to the Output ("translated") images
        pathmodel       (string) : Full path name to the Pix2Pix model checkpoint

    Returns:
        output_path (string) : Path to generated/translated images
    """

    # ------------------------------
    # In order to be able to convert
    #  a Python Function directly
    #  into a Kubeflow component,
    #   we need to move the python
    #  includes inside that python
    #  function.
    # ------------------------------
    import numpy as np
    import tensorflow as tf
    import os
    import json
    import time

    # The below tag comment is used by a tool script from this project to automatically nest
    # the python code of the imports function tagged KFP-NEST-IMPORT, just right after this tag.
    # This is only usefull when using the SDK's kfp.components.func_to_container_op method,
    # which allows to convert a Python function to a pipeline component and returns a factory function.
    #
    #KFP-NEST-HERE


    # ------------------------------
    #  Define some hyperparameters
    #   (Not managed as Kubeflow
    #      pipeline parameters)
    # ------------------------------
    BATCH_SIZE = 1


    # ------------------------------
    #   Restore the Pix2Pix GAN
    #
    #   Rebuild the Generator
    #   (Skip the Discriminator
    #       and Optimizers)
    # ------------------------------
    generator = Generator()

    # Layer objects in TensorFlow may delay the creation of variables
    # to their first call, when input shapes are available.
    img = generator(np.random.uniform(-127.5, 127.5, (1, 256, 256, 3)).astype(np.float32))

    # ------------------------------
    #   Restore the last Checkpoint
    #   (Skip the Discriminator
    #       and Optimizers)
    # -----------------------------

    # Configure the model checkpoints saving
    checkpoint = tf.train.Checkpoint(generator=generator)

    # Restoring the latest checkpoint
    manager = tf.train.CheckpointManager(checkpoint, directory=pathmodel,
                                         max_to_keep=1, checkpoint_name='ckpt')
    status = checkpoint.restore(manager.latest_checkpoint).expect_partial()

    if manager.latest_checkpoint:
        print("Model restored from {}".format(manager.latest_checkpoint))
    else:
        print("[WARNING] Initializing model from scratch.")

    # ------------------------------
    #       One step Inference
    #    nested Helper function
    # ------------------------------
    #@tf.function # Compile function into a graph for faster execution
    # TODO : Using Autograd does not seem to work with Checkpoint Restore ??
    def generate_image(img):
        """ Generate an image using the Pix2pix Generator """
        return generator(img, training=False)

    # ------------------------------
    #  Extract the Test Dataset
    #    from the TFRecords file
    # ------------------------------
    test_dataset = get_dataset(pathdataset, BATCH_SIZE, shuffle=False)

    # ------------------------------
    # Loop over the training batches
    # ------------------------------
    for image_features in test_dataset:

        # Loop over all images in the batch
        for record_idx in range(BATCH_SIZE):

            # ------------------------------
            #    Extract the individual
            #   features and  reconstruct
            #    the input images to feed
            #      the Neural Networks
            # ------------------------------
            a_image, b_image, file_name = decode_tfrecords_example(image_features, record_idx)
            
            print("Processing image ", file_name)

            # ------------------------------
            #  Apply same Data preparation,
            #  as for the training, on
            #  b_image - the input image -
            # (but without Data augmentation)
            #  in order to feed into the
            # Generator Neural Network Input
            # ------------------------------
            img_b = normalize(b_image)  #[ height, width, OUTPUT_CHANNELS]
            img_b = tf.image.resize(img_b, [256, 256])

            # Add a batch dimension to have 4D Tensor images to feed the Neural Network input
            img_b = tf.expand_dims(img_b , axis=0)  # [ 1, height, width, channel]

            # ------------------------------
            #     Generate output image
            #     - One step inference -
            # ------------------------------
            fake_b = generate_image(img_b)

            # ------------------------------
            #  Save the source, target
            #  and generated images to disk
            # (incl. decoding if necessary)
            # ------------------------------
            img_name = pathoutput + "/img_a-" + file_name + ".jpg"
            save_image(a_image, img_name)
            img_name = pathoutput + "/img_b-" + file_name + ".jpg"
            save_image(b_image, img_name)
            img_name = pathoutput + "/fake_b-" + file_name + ".jpg"
            save_image(fake_b, img_name)

    print("End of inference on Test Dataset")

    # ------------------------------
    #     Write the Output of the
    #   Kubeflow Pipeline Component
    # ------------------------------
    try:
        # This works only inside Docker containers
        with open('/output.txt', 'w') as f:
            f.write(pathoutput)

    except PermissionError:
        pass

    return pathoutput



# ---------
#   Main
# ---------
def main(argv):
    del argv  # Unused.

    test_pix2pix(FLAGS.pathdataset,FLAGS.pathoutput, FLAGS.pathmodel)


if __name__ == '__main__':

    flags.DEFINE_string('pathdataset', None, 'Full path name to the test dataset (TFRecords file)')
    flags.DEFINE_string('pathoutput', None, 'Pull path name to the Output ("translated") images')
    flags.DEFINE_string('pathmodel', None,  'Full path name to the Pix2Pix model checkpoint')

    FLAGS = flags.FLAGS

    app.run(main)
