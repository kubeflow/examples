from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import tensorflow as tf

import model 

flags = tf.app.flags

flags.DEFINE_string('checkpoint_dir', '/tmp/mnist-train',
                    """Directory where to read training checkpoints.""")
flags.DEFINE_string('output_dir', '/tmp/mnist_serving',
                    """Directory where to export inference model.""")
flags.DEFINE_integer('model_version', 1,
                     """Version number of the model.""")

FLAGS = flags.FLAGS


def main(unused_argv):
    # Ops: located on the worker specified with FLAGS.task_id
    with tf.Graph().as_default():
        x = tf.placeholder(tf.float32, [None, model.IMAGE_PIXELS * model.IMAGE_PIXELS], name="x")

        x, y, y_, cross_entropy = model.mnist_inference(FLAGS.hidden_units)

        values, indices = tf.nn.top_k(y, 10)
        table = tf.contrib.lookup.index_to_string_table_from_tensor(
            tf.constant([str(i) for i in xrange(10)]))
        prediction_classes = table.lookup(tf.to_int64(indices))

        saver = tf.train.Saver()
        with tf.Session() as sess:
            # Restore variables from training checkpoints.
            ckpt = tf.train.get_checkpoint_state(FLAGS.checkpoint_dir)
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(sess, ckpt.model_checkpoint_path)
                # Assuming model_checkpoint_path looks something like:
                #   /my-favorite-path/imagenet_train/model.ckpt-0,
                # extract global_step from it.
                global_step = ckpt.model_checkpoint_path.split('/')[-1].split('-')[-1]
                print('Successfully loaded model from %s at step=%s.' % (
                    ckpt.model_checkpoint_path, global_step))
            else:
                print('No checkpoint file found at %s' % FLAGS.checkpoint_dir)
                return

            export_path = os.path.join(
                tf.compat.as_bytes(FLAGS.output_dir),
                tf.compat.as_bytes(str(FLAGS.model_version)))
            print('Exporting trained model to', export_path)

            builder = tf.saved_model.builder.SavedModelBuilder(export_path)

            # Build the signature_def_map.
            classification_inputs = tf.saved_model.utils.build_tensor_info(
                x)
            classification_outputs_classes = tf.saved_model.utils.build_tensor_info(
                prediction_classes)
            classification_outputs_scores = tf.saved_model.utils.build_tensor_info(values)

            classification_signature = (
                tf.saved_model.signature_def_utils.build_signature_def(
                    inputs={
                        tf.saved_model.signature_constants.CLASSIFY_INPUTS:
                            classification_inputs
                    },
                    outputs={
                        tf.saved_model.signature_constants.CLASSIFY_OUTPUT_CLASSES:
                            classification_outputs_classes,
                        tf.saved_model.signature_constants.CLASSIFY_OUTPUT_SCORES:
                            classification_outputs_scores
                    },
                    method_name=tf.saved_model.signature_constants.CLASSIFY_METHOD_NAME))

            tensor_info_x = tf.saved_model.utils.build_tensor_info(x)
            tensor_info_y = tf.saved_model.utils.build_tensor_info(y)

            prediction_signature = (
                tf.saved_model.signature_def_utils.build_signature_def(
                    inputs={'images': tensor_info_x},
                    outputs={'scores': tensor_info_y},
                    method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME))

            legacy_init_op = tf.group(tf.tables_initializer(), name='legacy_init_op')
            builder.add_meta_graph_and_variables(
                sess, [tf.saved_model.tag_constants.SERVING],
                signature_def_map={
                    'predict_images':
                        prediction_signature,
                    tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY:
                        classification_signature,
                },
                legacy_init_op=legacy_init_op)

            builder.save()


if __name__ == "__main__":
    tf.app.run()
