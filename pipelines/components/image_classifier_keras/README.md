

# ML Pipeline - Image Classification using Keras

## License

Copyright 2018 Google LLC. All Rights Reserved.<br/>

Licensed under the Apache License, Version 2.0 (the "License");<br/>
you may not use this file except in compliance with the License.<br/>
You may obtain a copy of the License at<br/>

    http://www.apache.org/licenses/LICENSE-2.0<br/>

Unless required by applicable law or agreed to in writing, software<br/>
distributed under the License is distributed on an "AS IS" BASIS,<br/>
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.<br/>
See the License for the specific language governing permissions and<br/>
limitations under the License.<br/>

## Overview

This *ML pipeline* performs image classification on images using a Convolutional
Neural Network (CNN) in Keras.

## Intended Use

### Primary Use

Users of this template can preprocess and train collections of images for
classification. The trained classifier is saved as a keras model, which can then
be deployed into an application.


### Example Use Cases

This pipeline comes with two example use cases (Datasets): EMNIST and
Fruits-360. Both datasets have been used in competitions in Kaggle.

The EMNIST dataset is an extension of the MNIST dataset. It include
all lower and uppercase letters, along with digits, in the same 28x28 grayscale
format as MNIST. The dataset demonstrates classification of grayscale images in
a larger classification range (62 classes) and substantial size images in the
training set (800,000).

The Fruits-360 are color images of fruits and their varieties. The dataset
demonstrates classification involving subtle features, particularly in color shading
and texture of fruits of the same type (e.g., apples), but of different variety.

## Input

### Data

The pipeline supports training of JPG, PNG, and TIF images, in either color
(RGB) or grayscale (K).

Datasets must be in a directory structure, where the subdirectories
are the corresponding classes, and their contents are the images. The following
two directory layouts are recognized (supported):

*Combined Dataset (Training and Test)*

                       root
               /        |          \
              V         V           V
        class_1     class_2     ... class_n
        image(s)    image(s)        image(s)

*Separated Dataset*

                       root
                    /         \
                   V           V
            Training            Test
              /   \             /     \
            V      V           V       V
       class_1 ... class_N   class_1 .. class_n
       image(s)    image(s)  image(s)   image(s)

### Sample Datasets

EMNIST: gs://cloud-samples-data/air/fruits360/fruits360.zip

FRUITS360: gs//cloud-samples-data/air/fruits360/fruits360.zip


## Run-Time Parameters

### Required

      --name                the name of the dataset (emnist and fruits360 are reserved for example datasets)
      --training_data_path  the path to the training data

### Optional

      --test_data_path      the path to the test data (if not specified, 20% of training data is used as test).
      --gcs                 the location on GCS storage of the dataset to download and unzip.
      --local               used in conjunction with --gcs, where to extract the zip file to locally.
      --resize              the (height, width) to resize images to for training (defaults to 28,28 for grayscale and 100,100 for color)
      --colorspace          whether to process the images as COLOR or GRAYSCALE (default: COLOR)
      --num_epochs          number of training epochs (default: 10)
      --batch_size          the mini batch size (default: 128)

### Example Invocations

*EMNIST*

python task.py --name=emnist --gcs=gs://cloud-samples-data/air/emnist.zip --local=./tmp --training_data_path=./tmp/emnist

*Fruits360*

python task.py --name=fruits360 --gcs=gs://cloud-samples-data/air/fruits360.zip --local=./tmp --training_data_path=./tmp/fruits-360/Training --test_data_path=./tmp/fruits-360/Test

*Custom*
python task.py --name=my_dataset --training_data_path=./my_dataset/Training --colorspace=COLOR --resize=(224,224) --num_epochs=20 --batch_size=256

## Outputs

The trained Keras model is saved as an HDF5 file and can be reloaded (deployed)
using Keras. The model is saved in the same local directory where the pipeline
is ran as, where <name> is the parameter to --name:

        <name>.h5

## Detailed Description

The pipeline is sequenced in stages, which may be reconfigured and/or modified:

      driver (task.py) -> image preprocessing (openCV.py) -> hdf5 storage (hdf5.py) -> dynamic configuration of CNN and training (model.py)

Descriptions of processing steps can be found in the docstrings and comments in the aforementioned source. Details on construction and best practices can be found in the accompanying notebook directory. The notebooks additionally contain abstract factory (in-memory) and code generator (on-disk) generators for more complex CNNs.
