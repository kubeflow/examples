# coding=utf-8
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

"""Data download utilities."""

import os
from allensdk.api.queries.rma_api import RmaApi
import pandas as pd
import logging
import numpy as np
from allensdk.api.queries.image_download_api import ImageDownloadApi
from IPython.display import Image
import shutil
import numpy as np
import math
from PIL import Image
from io import BytesIO
import tensorflow as tf
import argparse
import tempfile

from kube import Job

from util import maybe_mkdir

flags = tf.app.flags

flags.DEFINE_string("data_root", "/mnt/nfs-1/datasets/alleninst/mouse",
                    "The root dataset path.")

flags.DEFINE_integer("num_sections", 5,
                     "Number of image sections to download.")

FLAGS = flags.FLAGS


def maybe_get_section_list(data_root, product_abbreviation="Mouse", num_rows="all"):
    """Retrieve a list of section datasets.
    
    Enforces file structure:
        data_root/
            meta/
                section_list.csv
    
    Equivalent to:
        http://api.brain-map.org/api/v2/data/query.xml?criteria=model::SectionDataSet,\
        rma::criteria,[failed$eq%27false%27],products[abbreviation$eq%27Mouse%27],\
        rma::options[num_rows$eq{num_rows}]

    """
    
    rma = RmaApi()
    
    meta_root = os.path.join(data_root, "meta")

    maybe_mkdir(meta_root)
    section_list_path = os.path.join(meta_root, "section_list_%s.csv" % num_rows)
    
    if os.path.exists(section_list_path):
        tf.logging.info("Section list found, skipping download.")
        data = pd.read_csv(section_list_path)
        return data
    
    criteria = ','.join([
        "[failed$in\'false\']",
        "products[abbreviation$eq\'%s\']" % product_abbreviation
    ])
    
    logging.info("Getting section list with criteria, num rows: %s, %s" % (criteria, num_rows))
    
    data = pd.DataFrame(
        rma.model_query('SectionDataSet',
                        criteria=criteria,
                        num_rows=num_rows))

    data.to_csv(section_list_path)

    return data


def maybe_get_image_list(section_dataset_id, data_root, num_rows="all", image_api_client=None):
    """Obtain a list of images given a section dataset ID.

    Enforces file structure:
        data_root/
            meta/
                image_list_for_section{section_dataset_id}.csv
            
    Equivalent to:
        http://api.brain-map.org/api/v2/data/query.json?q=model::SectionImage,\
        rma::criteria,[data_set_id$eq{section_dataset_id}],rma::options[num_rows$eq{num_rows}][count$eqfalse]
    
    """
    
    meta_root = os.path.join(data_root, "meta")
    maybe_mkdir(meta_root)
    section_list_path = os.path.join(meta_root, "image_list_for_section%s_%s.csv" % (section_dataset_id, num_rows))
    
    if os.path.exists(section_list_path):
        logging.info("Image list found for section id %s, skipping download." % section_dataset_id)
        data = pd.read_csv(section_list_path)
        return data
    
    tf.logging.info("Getting image list for section: %s" % section_dataset_id)

    if image_api_client is None:
        image_api_client = ImageDownloadApi()

    data = pd.DataFrame((image_api_client.section_image_query(section_dataset_id, num_rows=num_rows)))
    
    data.to_csv(section_list_path)
    
    tf.logging.info("Finished getting image list for section: %s" % section_dataset_id)
    
    return data


def maybe_download_image_dataset(image_list, image_dataset_id, data_root, image_api_client=None):
    """Given a list of image IDs, download the corresponding images.
    
    Enforces file structure:
        data_root/
            raw/
                section_id/
                    image_id/
                        image_id_raw.jpg

    """

    dataset_root = os.path.join(data_root, "raw", str(image_dataset_id))
    maybe_mkdir(dataset_root)
    
    if image_api_client is None:
        image_api_client = ImageDownloadApi()
    
    tf.logging.info("Starting download of %s images..." % len(image_list))
    num_images = len(image_list)
    output_paths = []
    
    for i, image_id in enumerate(image_list[:]["id"]):
        url = "http://api.brain-map.org/api/v2/section_image_download/%s" % image_id
        filename = "raw_%s.jpg" % image_id
        output_base = os.path.join(dataset_root, str(image_id))
        maybe_mkdir(output_base)
        output_path = os.path.join(output_base, filename)
        output_paths.append(output_path)
        if os.path.exists(output_path):
            tf.logging.info("Skipping download, image %s of %s at path %s already exists." % (i, num_images, output_path))
            continue
            
        tf.logging.info("Downloading image %s of %s to path %s" % (i, num_images, output_path))
        
        tmp_file = tempfile.NamedTemporaryFile(delete=False)

        image_api_client.retrieve_file_over_http(url, tmp_file.name)
        shutil.move(tmp_file.name, output_path)
    
    tf.logging.info("Finished downloading images.")
    
    return output_paths


def maybe_download_image_datasets(data_root, section_offset=0, num_sections=1, images_per_section="all"):
    """Maybe download all images from specified subset of studies."""
    
    section_list = maybe_get_section_list(data_root, num_rows=num_sections)
    total_num_sections = len(section_list)
    tf.logging.info("Obtained section list with %s num_sections" % total_num_sections)
    
    if section_offset > total_num_sections:
        raise ValueError("Can't apply offset %s for section list of length %s" % (section_offset, total_num_sections))
    end_index = section_offset + num_sections
    if end_index > total_num_sections:
        raise ValueError("Saw end_index, num_sections that index past num_sections, respectively: %s, %s, %s" % (end_index,
                                                                                                                 num_sections,
                                                                                                                 total_num_sections))
    
    section_list_subset = section_list["id"][section_offset:end_index]
    
    image_api_client = ImageDownloadApi()
    
    for image_dataset_id in section_list_subset:
        image_list = maybe_get_image_list(image_dataset_id, data_root, images_per_section, image_api_client)
        image_data_paths = maybe_download_image_dataset(image_list, image_dataset_id, data_root, image_api_client)

        
def _get_raw_file_paths(raw_data_root, prefix=None):
    """Searches first-level subdirectories of raw_data_root for files starting with prefix
    and returns their full path."""
    directories = os.listdir(raw_data_root)
    hits = []
    
    tf.logging.info(directories)
    
    for directory in directories:
        if directory != "raw":
            continue
        directory_path = os.path.join(raw_data_root, directory)
        tf.logging.info(directory_path)
        for subdir in os.listdir(directory_path):
            
            subdir_path = os.path.join(raw_data_root, directory, subdir)
            tf.logging.info("Building path list for raw images in %s" % subdir_path)
            
            for image_id in os.listdir(subdir_path):
                
                image_path = os.path.join(subdir_path, image_id, "%s_%s.jpg" % (prefix, image_id))
                
                if os.path.exists(image_path):
                    hits.append(image_path)
                
    return hits


def subimage_files_for_image_file(raw_image_path, metadata_base_path, xy_size=1024, max_num_submimages=None,
                                  subimage_format = "jpeg", strip_input_prefix=True):
    """
    
    raw_image_path: The name of the raw image
    metadata_base_path: The directory to which subimage path lists should be written.
    
    """

    image_dir, image_filename = os.path.split(raw_image_path)
    
    prefix = "%sx%s" % (xy_size, xy_size)

    if strip_input_prefix:
        image_filename = "_".join(image_filename.split("_")[1:])
    
    path_manifest_filename = ".".join([image_filename.split(".")[0], "csv"])
    path_manifest_filename = "_".join([prefix, "path_manifest", path_manifest_filename])
    path_manifest_path = os.path.join(metadata_base_path, path_manifest_filename)

    if os.path.exists(path_manifest_path):
        tf.logging.info("Skipping generation of subimages which already exist with path manifest: %s" % path_manifest_path)
        return

    tf.logging.info("Generating subimages for image at path: %s" % raw_image_path)
    img = Image.open(raw_image_path)
    img = np.float32(img)
    shape = np.shape(img)
    
    count = 0
    
    with open(path_manifest_path, "w") as path_manifest_file:
    
        for h_index in range(0, math.floor(shape[0]/xy_size)):
            h_offset = h_index * xy_size
            h_end = h_offset + xy_size - 1
            for v_index in range(0, math.floor(shape[1]/xy_size)):
                v_offset = v_index * xy_size
                v_end = v_offset + xy_size - 1

                subimage = np.uint8(np.clip(img[h_offset:h_end, v_offset:v_end]/255.0, 0, 1)*255)

                subimage_filename = "%s_%s_%s" % (prefix, count, image_filename)
                subimage_path = os.path.join(image_dir, subimage_filename)

                with open(subimage_path, "w") as f:
                    Image.fromarray(subimage).save(f, subimage_format)

                # Write the name of the generated subimage to the path manifest
                path_manifest_file.write(subimage_path + "\n")

                count += 1
                if max_num_submimages is not None and count >= max_num_submimages:
                    tf.logging.info("Reached maximum number of subimages: %s" % max_num_submimages)
                    return


def subimages_for_image_files(root_data_dir):
    
    meta_root = os.path.join(root_data_dir, "meta")
    
    # Gets all jpegs under current dir with prefix raw_
    image_path_list = _get_raw_file_paths(root_data_dir, prefix="raw")
    
    tf.logging.info(image_path_list)
        
    tf.logging.info("Producing subimages for # raw images: %s" % len(image_path_list))
    for image_file_path in image_path_list:
        subimage_files_for_image_file(image_file_path, meta_root)


if __name__ == '__main__':
    
    logging.getLogger().setLevel(logging.INFO)
     
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root", dest="data_root",
                        help=("Root path to save and access allen institute "
                              "histology data"))
    parser.add_argument("--num_sections", dest="num_sections",
                        default=1,
                        help="The number of image sections to download.")
    parser.add_argument("--images_per_section", dest="images_per_section",
                        default=1,
                        help="The number of images per section to download.")
    args, _ = parser.parse_known_args()

    maybe_download_image_datasets(args.data_root,
                                  section_offset=0,
                                  num_sections=args.num_sections,
                                  images_per_section=args.images_per_section)
    
    subimages_for_image_files(args.data_root)


