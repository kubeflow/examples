# Copyright 2018 Google LLC. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""
Image Processig module using OpenCV
"""

import os, time
import cv2
import numpy as np
import multiprocessing as mp

NORMAL_0_1  = 0
NORMAL_N1_1 = 1
STANDARD    = 2

GRAYSCALE   = cv2.IMREAD_GRAYSCALE
COLOR       = cv2.IMREAD_COLOR

def load_directory(dir, colorspace=COLOR, resize=(128,128), normal=NORMAL_0_1, flatten=False, datatype=np.float32, concurrent=1, verbose=False):
    """ Load and Process a dataset of images for training a neural network.
    Args:
        dir       : (str) A directory structure of images, where subfolders are the classes.
        colorspace: (int) the openCV flag for colorspace conversion.
        resize    : (tuple(int, int)) the new size of the image specified as (height, width).
        normal    : (int) flag for selecting the normalization method.
        flatten   : (bool) flag for selecting to flatten into 1D vector (True).
        datatype  : (type) the datatype to convert the raw pixel data to.
        concurrent: (int) the number of collections to process in parallel.
        verbose   : (bool) flag to display to console progress, warnings and errors.

    Returns:
        A list of tuples, where each tuple is the pair: processed images for a class, and the corresponding class.

    Raises:
        None.
    """
    if not os.path.isdir(dir):
        raise Exception('load_directory(): root dir is not a directory: ' + dir)

    start_time = time.time()

    # return object: set of collections and corresponding labels
    collections = []

    # concurrency setup
    pool = None
    if concurrent > 1:
        pool = mp.Pool(concurrent)

    # Add directory seperator, if not already
    if not dir.endswith('/'):
        dir += '/'
    # Iterate through all the subdirectories. These should be the classes (labels) and their corresponding contents
    # the images.
    subdirs = [dir + subdir for subdir in os.listdir(dir) ]
    for subdir in subdirs:
        # Process only subdirectories. For example, there maybe a license file under the root (parent) directory.
        if os.path.isdir(subdir):
            # Get all the files in the directory
            files = [subdir + '/' + file for file in os.listdir(subdir)]

            # Subdirectory name is the label for these images (collection)
            label = os.path.basename(subdir)
            try:
                # Load and process all the images for this collection (class)
                if pool:
                    pool.apply_async(load_files, (files, colorspace, resize, normal, flatten, datatype, label), callback=collections.append)
                else:
                    data, _, errors  = load_files(files, colorspace, resize, normal, flatten, datatype, label)

                    # Assemble a list of each collection and its label
                    collections.append( (data, label) )
                if verbose: print("Data Preprocessed:", subdir)
            except Exception as e:
                if verbose: print("ERROR: Unable to process images in Directory:", subdir, e)
        else:
            if verbose: print("WARNING: Directory entry is not a folder:", subdir)

    if pool:
        pool.close()
        pool.join()

    if verbose: print("Total Time:", time.time() - start_time)
    return collections

def load_files(files, colorspace=COLOR, resize=(128,128), normal=NORMAL_0_1, flatten=False, datatype=np.float32, label=None):
    """ Load a list of file paths and preprocess as images for a nerual network.
    Args:
        files     : (list(str)) a list of files paths of images (of the same classification).
        colorspace: (int) the openCV flag for colorspace conversion
        resize    : (tuple(int, int)) the new size of the image specified as (height, width)
        normal    : (int) flag for selecting the normalization method
        flatten   : (bool) flag for selecting to flatten into 1D vector (True)
        datatype  : (type) the datatype to convert the raw pixel data to
        label     : (str) the label (class) associated with the files (collection)

    Returns:
        A collection of images as a numpy array of matrices (each corresponding to an image) ready for feeding
        into the input vector of a neural network, and a list of errors for (if) any image failed to be processed.

    Raises:
        None.
    """
    images = []
    errors = []
    for file in files:
        try:
            # Read in an image from disk
            image = image_input(file, colorspace)
            # Resize the image for the target neural network
            images.append(image_resize(image, resize, flatten))
        except Exception as e:
            # Skip processing this image,
            # Keep a list of the images that failed to process and reason why
            errors.append( (file, e) )

    try:
        # Convert list of images into numpy multidimensional array
        images = np.asarray(images)
        # Normalize the images
        images = image_normalization(images, normal, datatype)
    except Exception as e:
        # this is a critical (unrecoverable) error
        return None, label, errors

    # Assemble a multidimensional numpy array of input vectors for this list of files.
    return images, label, errors


def image_normalization(images, normal=NORMAL_0_1, datatype=np.float32):
    """ Normalize the pixel values of a collection of images.
    Args:
        images  : (numpy) collection of images in raw pixel data as a numpy array of matrices (each corresponding to an image)
        normal  : (int) flag for selecting the normalization method
        datatype: (type) the datatype to convert the raw pixel data to
    Returns:
        A collection of normalized images as a numpy array of matrices (each corresponding to an image).
    Raises:
        ValueError: Invalid value for normal.
    """
    # This normalizes (scales pixel values) between the range 0 .. 255
    images = images.astype(datatype)
    if normal == NORMAL_0_1:
        images /= 255.0
    # This normalizes (scales pixel values) between the range -128 .. 127
    elif normal == NORMAL_N1_1:
        images = images / 127.5 - 1
    # This uses standardization, where pixel are scaled with a mean of 0 and standard deviation of 1
    elif normal == STANDARD:
        images = (images - images.mean()) / np.std(images)
        # the 1e-5 is to add a tiny amount to prevent the possibility of dividing by zero.
        #images = (images - images.mean()) / np.sqrt(images.var() + 1e-5)
    else:
        raise ValueError('normalization(): invalid parameter for normal: ' + str(normal))
    return images

def image_resize(image, resize=(128,128), flatten=False):
    """ Resize (downsample) an image for the target neural network
    Args:
        image : (numpy) an image in raw pixel data
        resize: (tuple(int, int)) the new size of the image specified as (height, width)
    Returns:
        The resized image as raw pixel data as numpy array

    Raises:
        Exception: Could not resize the image.
    """
    # size must be of type set and length two (i.e., (H, W))
    try:
        if flatten:
            return cv2.resize(image, resize, interpolation=cv2.INTER_AREA).flatten()
        return cv2.resize(image, resize, interpolation=cv2.INTER_AREA)
    except Exception as e:
      raise Exception('image_resize(): could not resize image to: ' + str(resize) + ': ' + str(e))


def image_input(file, colorspace=COLOR):
    """ Read an image in from disk and convert to specified color space.
    Args:
        file      : (str) file path to the image.
        colorspace: (int) the openCV flag for colorspace conversion.

    Returns:
        Uncompressed 'color converted' raw pixel data as numpy array

    Raises:
        Exception: could not read in image.
    """
    try:
        return cv2.imread(file, colorspace)
    except:
        raise Exception('image_input(): could not read in image: ' + file)
