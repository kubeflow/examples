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
"""

import h5py
import numpy as np

def store_dataset(name, dataset, verbose=False):
    """ Store a dataset of preprocessed image data to HDF5 file, where each HDF5 dataset is a collection of preprocessed
        images with the same label (class). The name of the HDF5 dataset is the label.
    Args:
        name   : (str) name of the dataset to use as the basename of the HDF5 file
        dataset: (list(tuple(numpy,list))) preprocessed dataset.
        verbose: (bool) display (print to console) the collections and labels written to the HDF5 file.
    Returns:
        Nothing

    Raises:
        None.
    """
    # Write the images and labels to disk as HD5 file
    with h5py.File(name + '.h5', 'w') as hf:
        for ix in range(0, len(dataset)):
            try:
                hf.create_dataset(dataset[ix][1], data=dataset[ix][0])
            except Exception as e:
                print(e)
                pass # what to do ?

    if verbose:
        with h5py.File(name + '.h5') as hf:
            print(list(hf.keys()))


def load_dataset(name):
    """ Load a dataset (machine learning ready data) from a HDF5 file.
    Args:
        name   : (str) name of the dataset to use as the basename of the HDF5 file.

    Return:
        The dataset as a multi-dimensional numpy array, the corresponding labels as a numpy multi-dimensional array,
        and the mapping of classes (names) to labels (integer values).

    Raises:
        None
    """

    collections=[]
    classes=[]

    # Read the images and labels from disk as HD5 file
    with h5py.File(name + '.h5', 'r') as hf:
        labels = list(hf.keys())
        for label in labels:
            collections.append( hf[label][:] )
            classes.append(label)

    # expand labels in each class to equal number of images per class
    new_labels = []
    for i in range(len(labels)):
        new_labels.append( np.full(len(collections[i]), i) )
    labels = np.concatenate(new_labels)

    # merge the collections together into a dataset
    collections = np.concatenate(collections)

    return collections, labels, classes
