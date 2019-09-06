from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl import app
from absl import flags

from utils import get_dataset, decode_tfrecords_example, transform_image         #KFP-NEST-IMPORT
from model import Generator, Discriminator, discriminator_loss, generator_loss   #KFP-NEST-IMPORT

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
def train_pix2pix(pathdataset: str, pathmodel: str, pathlogs: str, epochs: int = 150,
                  learningrate: float = 2e-4, batchsize: int = 1)-> str:
  """
  Train Pix2Pix.

  Args:
    pathdataset      (string) : Full path name to the training dataset (TFRecords file)
    pathmodel        (string) : Full path name to the Pix2Pix model checkpoint
    pathlogs         (string) : Full path name to the Tensorboard logs directory
    epochs           (int)    : Number of training epochs
    learningrate     (float)  : Learning rate (for generator and discriminator)
    batchsize        (int)    : Batch size

  Returns:
    model            (string) : Full path name to the Pix2Pix model checkpoint
  """

  # ------------------------------
  # In order to be able to convert
  #  a Python Function directly
  #  into a Kubeflow component,
  #   we need to move the python
  #  includes inside that python
  #  function.
  # ------------------------------
  import tensorflow as tf
  import json
  import time

  # The below tag comment is used by a tool script from this project to automatically nest
  # the python code of the imports function tagged KFP-NEST-IMPORT, just right after this tag.
  # This is only usefull when using the SDK's kfp.components.func_to_container_op method,
  # which allows to convert a Python function to a pipeline component and returns a factory function
  #
  #KFP-NEST-HERE

  # ------------------------------
  #  Define some hyperparameters
  #   (Not managed as Kubeflow
  #      pipeline parameters)
  # ------------------------------
  BETA_1 = 0.5        # Exponential decay rate for the 1st moment estimates


  # ------------------------------
  #   Get ready for Training
  # ------------------------------

  # Build the Pix2Pix GAN
  generator = Generator()
  discriminator = Discriminator()

  # Set the Optimizers
  generator_optimizer = tf.keras.optimizers.Adam(learningrate, BETA_1)
  discriminator_optimizer = tf.keras.optimizers.Adam(learningrate, BETA_1)

  # Configure the model checkpoints saving
  checkpoint = tf.train.Checkpoint(generator_optimizer=generator_optimizer,
                   discriminator_optimizer=discriminator_optimizer,
                   generator=generator,
                   discriminator=discriminator)
  manager = tf.train.CheckpointManager(checkpoint, directory=pathmodel,
                     max_to_keep=1, checkpoint_name='ckpt')
  _ = checkpoint.restore(manager.latest_checkpoint)

  if manager.latest_checkpoint:
    print("Model restored from {}".format(manager.latest_checkpoint))
  else:
    print("Initializing from scratch.")


  # Configure a summary writer to collect Tensorboard logs
  summary_writer = tf.summary.create_file_writer(pathlogs)


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


  # ------------------------------
  #       One step Training
  #    nested Helper function
  # ------------------------------
  @tf.function # Compile function into a graph for faster execution
  def train_step(input_image, target):
    '''
    Perform one training step

    Args:
      input_image   : Input image
      target        : Output image (ground thruth)

    Returns:
      gen_loss    : Generator loss
      disc_loss   : Dicriminator loss

    '''
    with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape:

      # Compute the Generator output
      gen_output = generator(input_image, training=True)

      # Compute the Discriminator output for real and generated inputs
      disc_real_output = discriminator([input_image, target], training=True)
      disc_generated_output = discriminator([input_image, gen_output], training=True)

      # Computes the Generator and Discriminator losses
      gen_loss = generator_loss(disc_generated_output, gen_output, target)
      disc_loss = discriminator_loss(disc_real_output, disc_generated_output)


    # Apply Gradient Descent
    generator_gradients = gen_tape.gradient(gen_loss,
                        generator.trainable_variables)
    discriminator_gradients = disc_tape.gradient(disc_loss,
                           discriminator.trainable_variables)

    generator_optimizer.apply_gradients(zip(generator_gradients,
                        generator.trainable_variables))
    discriminator_optimizer.apply_gradients(zip(discriminator_gradients,
                          discriminator.trainable_variables))

    return gen_loss, disc_loss, gen_output


  # ------------------------------
  #        TRAINING LOOP
  # ------------------------------
  for epoch in range(epochs):

    start = time.time()

    # ------------------------------
    #  Extract the Training Dataset
    #    from the TFRecords file
    # ------------------------------
    training_dataset = get_dataset(pathdataset, batchsize)

    # ------------------------------
    # Loop over the training batches
    # ------------------------------
    for image_features in training_dataset:

      # Loop over all images in the batch
      for record_idx in range(batchsize):

        # ------------------------------
        #    Extract the individual
        #   features and  reconstruct
        #    the input images to feed
        #      the Neural Networks
        # ------------------------------
        a_image, b_image, _ = decode_tfrecords_example(image_features, record_idx)

        # ------------------------------
        #   Perform Data Augmentation
        #     with the input images
        # ------------------------------
        a_image, b_image = transform_image(a_image, b_image)

        # ------------------------------
        #  Perform one TRAININING STEP
        # ------------------------------
        gen_loss, disc_loss, gen_output = train_step(input_image=b_image, target=a_image)



    # ------------------------------
    #  Write tensorboard summaries
    #   at the end of the epoch
    # ------------------------------
    with summary_writer.as_default():
      tf.summary.scalar('Generator loss', gen_loss, step=epoch)
      tf.summary.scalar('Discriminator loss', gen_loss, step=epoch)
      tf.summary.image('input_image', b_image, max_outputs=epoch, step=epoch)
      tf.summary.image('target_image', a_image, max_outputs=epoch, step=epoch)
      tf.summary.image('generated_image', gen_output, max_outputs=epoch, step=epoch)

    # ------------------------------
    # Saving (checkpoint) the model
    #        every 10 epochs
    # ------------------------------
    if (epoch + 1) % 10 == 0:
      manager.save()

    # ------------------------------
    #      Display progression
    # ------------------------------
    print('Epoch {}/{} ( {:.1f} sec)  gen_loss={:.6f}  disc_loss={:.6f}'
       .format(epoch + 1, epochs, time.time()-start, gen_loss, disc_loss))

  print("End of training")

  # ------------------------------
  #     Write the Output of the
  #   Kubeflow Pipeline Component
  # ------------------------------
  try:
    # This works only inside Docker containers
    with open('/output.txt', 'w') as f:
      f.write(pathmodel)

  except PermissionError:
    pass

  return pathmodel



# ---------
#   Main
# ---------
def main(argv):
  del argv  # Unused.

  train_pix2pix(FLAGS.pathdataset, FLAGS.pathmodel, FLAGS.pathlogs,
          FLAGS.epochs, FLAGS.learningrate, FLAGS.batchsize)


if __name__ == '__main__':

  flags.DEFINE_string('pathdataset', None, 'Full path name to the training dataset (TFRecords)')
  flags.DEFINE_string('pathmodel', None, 'Full path name to the Pix2Pix model checkpoint')
  flags.DEFINE_string('pathlogs', None, 'Full path name to the Tensorboard log directory')
  flags.DEFINE_integer('epochs', 200, 'Number of training epochs')
  flags.DEFINE_float('learningrate', 2e-4, 'Learning rate (for generator and discriminator)')
  flags.DEFINE_integer('batchsize', 1, 'Batch size')

  FLAGS = flags.FLAGS

  app.run(main)
