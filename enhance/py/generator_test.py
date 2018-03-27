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

import unittest
from generator import AllenBrainImg2img, _generator
import tempfile


class TestGenerator(unittest.TestCase):
    
    def test_null(self):
        
        tmpd = tempfile.mkdtemp()
        _generator(tmpd, 1)


class TestAllenBrainImg2img(unittest.TestCase):
    
    def test_instantiate(self):
        
        problem = AllenBrainImg2img()


if __name__ == "__main__":
    unittest.main()