from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt


#------------------------------------------------
#  Helper function to resize and perform
#  data augmentation before feeding the input
#  of the neural networks
#------------------------------------------------

def transform_image(img_a, img_b, initial_resize=286, crop_resize=256):
    """
    Resize a pair of  input/target Tensor Images to meet the
    Neural Network input size. It can also apply Data augmentation
    by by randomly resizing and cropping the pair of
    input/target Tensor images

    If crop_resize = 0 , then only resizing is applied
    If initial_resize > crop_resize, then Data augmentation is applied

    Args:
        img_a : 3D tf.float32 Tensor image
        img_b : 3D tf.float32 Tensor image
        initial_resize (int) : Initial resizing before Data augmentation
        crop_resize (int) : Final image size after random cropping

    Returns:
        img_a, img_b : Normalized 4D tf.float32 Tensors [ 1, height, width, channel ]
                       (with width = height = crop_resize)
    """

    #..........................................
    #  Transform_image nested helper functions
    #..........................................
    def _normalize(image):
        """ Normalize a 3D Tensor image """
        return (image / 127.5) - 1


    def _resize(img_a, img_b, size):
        """ Resize a pair of Input/Target 3D Tensor Images """
        img_a = tf.image.resize(img_a, [size, size])
        img_b = tf.image.resize(img_b, [size, size])
        return img_a, img_b


    def _dataset_augment(img_a, img_b, initial_resize, crop_resize):
        """ Dataset augmentation (random resize+crop) of a pair of source/target 3D Tensor images """

        # Resize image to size [initial_resize,  initial_resize, 3 ]
        img_a, img_b = _resize(img_a, img_b, initial_resize)

        # Random cropping to size [crop_resize,  crop_resize, 3 ]
        # Images are staked to preserve source/target relationship
        stacked_images = tf.stack([img_a, img_b], axis=0) # size [2, h, w, ch]
        cropped_images = tf.image.random_crop(stacked_images,
                                              size=[2, crop_resize, crop_resize, 3])
        img_a, img_b = cropped_images[0], cropped_images[1]

        # Random mirorring of the images
        if np.random.rand() > 0.5:
            img_a = tf.image.flip_left_right(img_a)
            img_b = tf.image.flip_left_right(img_b)

        return img_a, img_b

    
    #..........................................
    #  Transform_image Main
    #..........................................

    # Normalize the Image Tensors
    img_a, img_b = _normalize(img_a), _normalize(img_b) # [ height, width, channel]

    # Check if data augmentation can be used
    if (initial_resize > crop_resize) and (crop_resize > 0):
        # Aply data augmenation
        img_a, img_b = _dataset_augment(img_a, img_b, initial_resize, crop_resize)
    else:
        # Just Resize image to size [initial_resize,  initial_resize, 3 ]
        img_a, img_b = _resize(img_a, img_b, initial_resize)

    # WIP Add a batch dimension to have 4D Tensor images
    #img_a = tf.expand_dims(img_a , axis=0)  # [ 1, height, width, channel]
    #img_b = tf.expand_dims(img_b , axis=0)  # [ 1, height, width, channel]

    return img_a, img_b



def get_dataset(path_to_tfrecords):
    """
    Read a TFRecords file and return a parsed Tensorflow Dataset

    Args:
        path_to_tfrecords  (String) : Full path to the TFRecords file containing the dataset
        
    Returns:
        dataset   (tf.data.Dataset)  : Return a parsed Tensorflow Dataset
    """

    # Create a Dataset from the TFRecord file
    raw_image_dataset = tf.data.TFRecordDataset(path_to_tfrecords)

    # Parse each example to extract the features
    feature = { 'jpeg_file' : tf.io.FixedLenFeature([], tf.string),
                'height': tf.io.FixedLenFeature([], tf.int64),
                'width': tf.io.FixedLenFeature([], tf.int64),
                'depth': tf.io.FixedLenFeature([], tf.int64),
                'raw_img_a': tf.io.FixedLenFeature([], tf.string),
                'raw_img_b': tf.io.FixedLenFeature([], tf.string)
    }

    def _parse_image_function(example_proto):
        return tf.io.parse_single_example(example_proto, feature)


    parsed_image_dataset = raw_image_dataset.shuffle(400)
    parsed_image_dataset = parsed_image_dataset.map(_parse_image_function,
                                      num_parallel_calls=tf.data.experimental.AUTOTUNE)

    return parsed_image_dataset



def decode_tfrecords_example(image_features):
    """
    Decode a parsed dataset example into the corresponding image pair

    Args:
        image_features  (Dict) : One example of a parsed dataset
        
    Returns:
        a_image, b_image  (Tensor) : Normalized 3D tf.float32 Tensors [ height, width, channel ]
        
    """
    # Extract the individual features and  reconstruct

    width = int(image_features['width'])
    height = int(image_features['height'])
    depth = int(image_features['depth'])
    raw_img_a = image_features['raw_img_a'].numpy()    
    raw_img_b = image_features['raw_img_b'].numpy()

    a_image = np.frombuffer(raw_img_a, dtype=np.uint8)
    a_image = a_image.reshape((height,width,depth))

    b_image = np.frombuffer(raw_img_b, dtype=np.uint8)
    b_image = b_image.reshape((height,width,depth))
    
    return a_image, b_image



def display_img(img_a, img_b, normalized=True):
    """
    Display a pair of image

    Args:
        img_a      (Tensor) : 3D tf.float32 Tensors [ height, width, channel ]
        img_b      (Tensor) : 3D tf.float32 Tensors [ height, width, channel ]
        normalized (Bool)   : True = remove normalization
        
    """    
    # Remove normalization
    if normalized:
        img_a=np.uint8(img_a*127.5 + 127.5)
        img_b=np.uint8(img_b*127.5 + 127.5)
        
    # Display pictures    
    plt.figure(figsize=(7,7))
    ax = plt.subplot(121)       
    ax.imshow(np.uint8(img_a))
    ax.set_title("img_a")
    ax = plt.subplot(122)
    ax.imshow(np.uint8(img_b))
    ax.set_title("img_b")        
    plt.show()
    plt.close()