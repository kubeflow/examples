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

"""Tests of general utilities."""

import unittest
import tempfile

from util import object_as_dict, expect_path, expect_type, dict_prune_private


class MyClassOne(object):

    def __init__(self):
        self.attr_refs_dict = {
            "hello": "world"
        }

class MyClassTwo(object):

    def __init__(self):
        
        self.attr_refs_dict = {
            "hello": "world"
        }
        self.attr_refs_list = [
            "hello", "world"
        ]
        self.attr_refs_obj = MyClassOne()


class TestObjectAsDict(unittest.TestCase):
    
    def test_nested_list(self):
        
        instance = MyClassTwo()
        cases = [
            {
                "input": [{"hello": "world"}],
                "output": [{"hello": "world"}]
            },
            {
                "input": [{"hello": "world"}],
                "output": [{"hello": "world"}]
            },
            {
                "input": instance,
                "output": {
                    "attr_refs_dict": {
                        "hello": "world"
                    },
                    "attr_refs_list": [
                        "hello", "world"
                    ],
                    "attr_refs_obj": {
                        "attr_refs_dict": {
                            "hello": "world"
                        }
                    }
                }
            }
        ]
        
        for case in cases:
            self.assertEqual(object_as_dict(case["input"]), case["output"])


class TestDictPrunePrivate(unittest.TestCase):
    
    def test_simple(self):
        
        cases = [
            {
                "input": {
                    "key": "value",
                    "_ignore": "me",
                    "_also_ignore": {
                        "this": "subtree"
                    },
                    "keep": {
                        "this": "subtree"
                    }
                },
                "expected": {
                    "key": "value",
                    "keep": {
                        "this": "subtree"
                    }
                }
            }
        ]
        for case in cases:
            pruned = dict_prune_private(case["input"])
            self.assertEqual(pruned, case["expected"])
        
            
class TestExpect(unittest.TestCase):
    
    def test_expect_path(self):
        tmpd = tempfile.mkdtemp()
        expect_path(tmpd)
    
    def test_expect_type(self):
        expect_type("hello world", str)
    

if __name__ == "__main__":
    unittest.main()