from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

#KFP-BEGIN

import os
import glob
from PIL import Image
import matplotlib.pyplot as plt

import numpy as np
import tensorflow as tf


#------------------------------------------------
#  Helper functions to resize and perform
#  data augmentation before feeding the input
#  of the neural networks
#------------------------------------------------

def normalize(image):
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
  # Normalize the Image Tensors
  img_a, img_b = normalize(img_a), normalize(img_b) # [ height, width, channel]

  # Check if data augmentation can be used
  if (initial_resize > crop_resize) and (crop_resize > 0):
    # Aply data augmenation
    img_a, img_b = _dataset_augment(img_a, img_b, initial_resize, crop_resize)
  else:
    # Just Resize image to size [initial_resize,  initial_resize, 3 ]
    img_a, img_b = _resize(img_a, img_b, initial_resize)

  # Add a batch dimension to have 4D Tensor images
  img_a = tf.expand_dims(img_a, axis=0)  # [ 1, height, width, channel]
  img_b = tf.expand_dims(img_b, axis=0)  # [ 1, height, width, channel]

  return img_a, img_b



def get_dataset(path_to_tfrecords, batch_size=1, buffer_size=400, shuffle=True):
  """
  Read a TFRecords file and return a parsed Tensorflow Dataset

  Args:
    path_to_tfrecords  (String) : Full path to the TFRecords file containing the dataset
    batch_size         (int)    : Batch size
    buffer_size        (int)    : Buffer size to shuffle the data

  Returns:
    dataset   (tf.data.Dataset)  : Return a parsed Tensorflow Dataset
  """

  # ------------------------------
  #      Helper Function to
  #    parse the TFRecord file
  # ------------------------------
  feature = {'jpeg_file' : tf.io.FixedLenFeature([], tf.string),
        'height': tf.io.FixedLenFeature([], tf.int64),
        'width': tf.io.FixedLenFeature([], tf.int64),
        'depth': tf.io.FixedLenFeature([], tf.int64),
        'raw_img_a': tf.io.FixedLenFeature([], tf.string),
        'raw_img_b': tf.io.FixedLenFeature([], tf.string)
  }

  def _parse_image_function(example_proto):
    return tf.io.parse_single_example(example_proto, feature)

  # ------------------------------
  #    Read the TFRecords file
  #  and return a Dataset object
  # ------------------------------
  dataset = tf.data.TFRecordDataset(path_to_tfrecords)
  if shuffle:
    dataset = dataset.shuffle(buffer_size)
  dataset = dataset.map(_parse_image_function,
              num_parallel_calls=tf.data.experimental.AUTOTUNE)
  dataset = dataset.batch(batch_size)
  dataset = dataset.prefetch(tf.data.experimental.AUTOTUNE)

  return dataset




def decode_tfrecords_example(image_features, record_idx):
  """
  Decode a parsed dataset example into the corresponding image pair

  Args:
    image_features  (Dict) : One batch of parsed dataset examples
    record_idx      (int)  : Index of the record to process in the batch


  Returns:
    a_image, b_image  (Tensor) : Normalized 3D tf.float32 Tensors [ height, width, channel ]
    name              (String) : File name of the image used  in the source dataset
                   (without file extension)

  """
  # Extract the individual features and  reconstruct

  file_name = image_features['jpeg_file'][record_idx].numpy()
  width = int(image_features['width'][record_idx])
  height = int(image_features['height'][record_idx])
  depth = int(image_features['depth'][record_idx])
  raw_img_a = image_features['raw_img_a'][record_idx].numpy()
  raw_img_b = image_features['raw_img_b'][record_idx].numpy()

  a_image = np.frombuffer(raw_img_a, dtype=np.uint8)
  a_image = a_image.reshape((height, width, depth))

  b_image = np.frombuffer(raw_img_b, dtype=np.uint8)
  b_image = b_image.reshape((height, width, depth))

  name = file_name.decode("utf-8")
  name = os.path.splitext(name)[0]

  #DEBUG
  a_image = tf.cast(a_image, tf.float32)
  b_image = tf.cast(b_image, tf.float32)

  return a_image, b_image, name



def save_image(img, image_name):
  """
  Helper function to Save a Tensor/Numpy image array to disk.

  Automatic decoding allossssssssssss
    - Drop batch dimension if present in the Image Tensor
    - Reverse Normalization before saving the image to disk
    - Convert from Tensor to Numpy format

  Args:
    img         (Tensor) : 3D or 4D Image Tensor
    image_name    (str)  : Image full pathname
  """

  # Convert from Tensor to Numpy array
  if not isinstance(img, np.ndarray):
    img = img.numpy()

  # Drop the batch dimension
  if len(img.shape) == 4:
    img = np.squeeze(img, axis=0)

  # Reverse the normalization process
  max_val = np.amax(img)
  if np.any((max_val < 1)&(max_val > -1)):
    img = (img * 127.5) + 127.5

  # Cast output to uint8
  img = img.astype(np.uint8).clip(0, 255)

  # Write image to disk
  plt.imsave(image_name, img)



def display_results(path_to_images, display_max_examples=3, reverse=True):
  '''
  Display a few image examples from the the Dataset Input/target
  and associated Generated images from the Pix2Pix GAN generator

  Args:
    path_to_ouputs       (str)  : path to the Pix2Pix outputs
    display_max_examples (int)  : Number of samples to display (0 to display all)
    reverse              (bool) : False = oldest images first and vice-versa
  '''

  # During the testing task, images are saved to disk in the following order :
  # img_a, img_b and fake_b. Thus we can compute list of picture files from latest
  # to oldest or vice-versa
  images_a = [s for s in glob.glob(path_to_images + "/img_a*") if os.path.isfile(s)]
  images_a.sort(key=lambda s: os.path.getmtime(s), reverse=reverse)

  images_b = [s for s in glob.glob(path_to_images + "/img_b*") if os.path.isfile(s)]
  images_b.sort(key=lambda s: os.path.getmtime(s), reverse=reverse)

  images_fake = [s for s in glob.glob(path_to_images + "/fake_b*") if os.path.isfile(s)]
  images_fake.sort(key=lambda s: os.path.getmtime(s), reverse=reverse)

  # Display the pictures in a grid
  for idx, (a, f, b) in enumerate(zip(images_a, images_fake, images_b)):

    if (idx == display_max_examples) and (idx != 0):
      #Enough images have been displayed
      break

    img_a = np.array(Image.open(a))
    img_fake = np.array(Image.open(f))
    img_b = np.array(Image.open(b))
    title = os.path.basename(os.path.splitext(b)[0]).split('-')[-1]

    plt.figure(figsize=(10, 10))
    ax = plt.subplot(131)
    ax.imshow(img_b)
    ax.set_title("Source: " + title)
    ax = plt.subplot(132)
    ax.imshow(img_fake)
    ax.set_title("Generated: " + title)
    ax = plt.subplot(133)
    ax.imshow(img_a)
    ax.set_title("Target: " + title)

    plt.show()
    plt.close()

#KFP-END
