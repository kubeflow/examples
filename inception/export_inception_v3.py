import os
from six.moves import urllib

import tensorflow as tf
import tensorflow.contrib.slim as slim
from tensorflow.contrib.slim.python.slim.nets import inception_v3

tf.app.flags.DEFINE_string('checkpoint', '/tmp/inception_v3.ckpt',
                           """Checkpoint file.""")
tf.app.flags.DEFINE_string('output_dir', '/tmp/inception_output',
                           """Directory where to export inference model.""")
tf.app.flags.DEFINE_integer('model_version', 1,
                            """Version number of the exported model.""")
tf.app.flags.DEFINE_integer('image_size', 299,
                            """Image Size""")
tf.app.flags.DEFINE_integer('num_classes', 1000,
                            """Number of image classes.""")
tf.app.flags.DEFINE_integer('top_k', 5,
                            """Top K classes for prediction.""")
tf.app.flags.DEFINE_string('imagenet_label_base_url', 'https://raw.githubusercontent.com/tensorflow/serving/master/tensorflow_serving/example/',
                            """Imagenet label base url.""")


FLAGS = tf.app.flags.FLAGS


def create_readable_names_for_imagenet_labels():
    synset_url = '{}/imagenet_lsvrc_2015_synsets.txt'.format(FLAGS.imagenet_label_base_url)
    synset_to_human_url = '{}/imagenet_metadata.txt'.format(FLAGS.imagenet_label_base_url)
    
    filename, _ = urllib.request.urlretrieve(synset_url)
    synset_list = [s.strip() for s in open(filename).readlines()]
    num_synsets_in_ilsvrc = len(synset_list)
    assert num_synsets_in_ilsvrc == FLAGS.num_classes
    
    filename, _ = urllib.request.urlretrieve(synset_to_human_url)
    synset_to_human_list = open(filename).readlines()
    num_synsets_in_all_imagenet = len(synset_to_human_list)
    assert num_synsets_in_all_imagenet == 21842
    
    synset_to_human = {}
    for s in synset_to_human_list:
        parts = s.strip().split('\t')
        assert len(parts) == 2
        synset = parts[0]
        human = parts[1]
        synset_to_human[synset] = human
    
    label_index = 1
    labels_to_names = {'0': 'background'}
    for synset in synset_list:
        name = synset_to_human[synset]
        labels_to_names[str(label_index)] = name
        label_index += 1
    
    return labels_to_names

def model(images):
    # Run inference.
    names = create_readable_names_for_imagenet_labels()
    table = tf.contrib.lookup.HashTable(tf.contrib.lookup.KeyValueTensorInitializer(names.keys(), 
                                                      names.values(), 
                                                      key_dtype=tf.string, 
                                                      value_dtype=tf.string), 
                          default_value='background')

    with slim.arg_scope(inception_v3.inception_v3_arg_scope()):
        logits, endpoints = inception_v3.inception_v3(images, FLAGS.num_classes + 1, False)
        probabilities = tf.nn.softmax(logits)
        top_pred = tf.nn.top_k(tf.squeeze(probabilities), k=FLAGS.top_k, name="top_predictions")
        names = table.lookup(tf.as_string(top_pred.indices))
        values = top_pred.values
    return names, values


def preprocess_image(image_buffer):
    """Preprocess JPEG encoded bytes to 3D float Tensor."""

    # Decode the string as an RGB JPEG.
    # Note that the resulting image contains an unknown height and width
    # that is set dynamically by decode_jpeg. In other words, the height
    # and width of image is unknown at compile-time.
    image = tf.image.decode_jpeg(image_buffer, channels=3)
    # After this point, all image pixels reside in [0,1)
    # until the very end, when they're rescaled to (-1, 1).  The various
    # adjust_* ops all require this range for dtype float.
    image = tf.image.convert_image_dtype(image, dtype=tf.float32)
    # Crop the central region of the image with an area containing 87.5% of
    # the original image.
    image = tf.image.central_crop(image, central_fraction=0.875)
    # Resize the image to the original height and width.
    image = tf.expand_dims(image, 0)
    image = tf.image.resize_bilinear(
        image, [FLAGS.image_size, FLAGS.image_size], align_corners=False)
    image = tf.squeeze(image, [0])
    # Finally, rescale to [-1,1] instead of [0, 1)
    image = tf.subtract(image, 0.5)
    image = tf.multiply(image, 2.0)
    return image

def export():
    with tf.Graph().as_default():
        # Build inference model.
        # Please refer to Tensorflow inception model for details.

        # Input transformation.
        image_contents = tf.placeholder(tf.string, shape=[None])

        images = tf.map_fn(preprocess_image, image_contents, dtype=tf.float32)
        
        names, values = model(images)


        # Restore variables from training checkpoint.
        model_variables = slim.get_model_variables('InceptionV3')

        saver = tf.train.Saver(model_variables, reshape=False)

        with tf.Session() as sess:
            # Restore variables from training checkpoints.
            saver.restore(sess, FLAGS.checkpoint)

            # Export inference model.
            output_path = os.path.join(
                tf.compat.as_bytes(FLAGS.output_dir),
                tf.compat.as_bytes(str(FLAGS.model_version)))
            print('Exporting trained model to %s' % output_path)
            builder = tf.saved_model.builder.SavedModelBuilder(output_path)

            # Build the signature_def_map.
            input_tensor_info = tf.saved_model.utils.build_tensor_info(
                image_contents)
            label_info = tf.saved_model.utils.build_tensor_info(
                names)
            prob_info = tf.saved_model.utils.build_tensor_info(
                values)

            classification_signature = (
                tf.saved_model.signature_def_utils.build_signature_def(
                    inputs={
                        'image_contents':
                            input_tensor_info,
                    },
                    outputs={
                        'labels':
                            label_info,
                        'probs':
                            prob_info,
                    },
                    method_name=tf.saved_model.signature_constants.
                    CLASSIFY_METHOD_NAME))

            legacy_init_op = tf.group(
                tf.tables_initializer(), name='legacy_init_op')
            builder.add_meta_graph_and_variables(
                sess, [tf.saved_model.tag_constants.SERVING],
                signature_def_map={
                    tf.saved_model.signature_constants.
                    DEFAULT_SERVING_SIGNATURE_DEF_KEY:
                        classification_signature,
                },
                legacy_init_op=legacy_init_op)

            builder.save()
            print('Successfully exported model to %s' % FLAGS.output_dir)

def main(_):
    export()


if __name__ == '__main__':
    tf.app.run()
