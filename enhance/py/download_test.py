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

"""Tests of data download utilities."""

import unittest
from download import maybe_get_section_list, maybe_get_image_list, maybe_download_image_dataset


class TestMaybeDownloadImageDataset(unittest.TestCase):
    
    def test_e2e_tiny(self):
        
        data_root = "/mnt/nfs-1/test"
        
        sl = maybe_get_section_list(data_root, product_abbreviation="Mouse", num_rows=1)
        
        section_dataset_id = "69526552"
        # Within this section dataset there is an image with ID 69481284
        
        image_list = maybe_get_image_list(sl[0])
        
        ## TODO: This is not working yet.
        
        #output_paths = maybe_download_image_dataset(image_list,
        #                                            image_dataset_id,
        #                                            data_root,
        #                                            image_api_client=None)
        
        #for op in output_paths:
        #    self.assertTrue(os.path.exists(op))


class TestGetRawFilePaths(unittest.TestCase):
    """It might be more worthwhile to use hdf5 than to test the hell out of this approach."""
    pass


class TestGenerateSubimages(unittest.TestCase):
    """Tests of utility for generating subimages from a larger image."""
    
    def test_generated_subimage_files_exist(self):
        """Generate subimages and check the resultant filenames exist."""
        pass
        #subimage_files_for_image_file(raw_image_path, metadata_base_path, xy_size=1024, max_num_submimages=None,
        #                              subimage_format = "jpeg", strip_input_prefix=True):
        #TODO: I don't like the path manifest approach being used here. Should use hdf5 or similar.
