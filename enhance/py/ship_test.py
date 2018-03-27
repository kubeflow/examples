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
import tempfile
import os
import logging

from ship import gcb_build_and_push, generate_image_tag, ftl_build_and_push

#TODO: Change this to be something that is accessible by presubmit test runner.
# Also will need to change auth method unless creds are manually added to 
# test runner ~/.docker/config.json...
_TESTING_PROJECT = "gcrpushtest"

class TestGCBBuildAndPush(unittest.TestCase):
    
    def setUp(self):
        """Set up local dummy build dir."""

        # Create a tmpdir locally, write a dummy dockerfile to it.
        self.tmpd = tempfile.mkdtemp()
        with open(os.path.join(self.tmpd, "Dockerfile"), "w") as out:
            out.write("FROM ubuntu")

    #def test_simple(self):
    #    
    #    tag = generate_image_tag(_TESTING_PROJECT, "test-ship")
    #    last_cache_from = "ubuntu"
    #    gcb_build_and_push(tag, self.tmpd, last_cache_from)


class TestFTLBuildAndPush(unittest.TestCase):
    
    def setUp(self):
        """Set up local dummy build dir."""

        # Create a tmpdir locally, write a dummy reqs file to it.
        self.build_dir = tempfile.mkdtemp()

    def test_simple(self):
        
        # TODO: This test verifies for various dependency cases FTL runs without
        # error but does not check whether the depedencies that succeeded can be
        # imported and used. When working with the bazel docker build rule found
        # that was able to build container that supposedly included tensorflow
        # and t2t but these could not be imported (whereas others such as flask
        # and tensorboard could be).
        
        tag = generate_image_tag(_TESTING_PROJECT, "test-ship-ftl")
        
        base_args = {
            'ftl_path': '/home/jovyan/work/tools/ftl.par',
            'virtualenv_path': '/usr/local/bin/virtualenv',
            'image_base_tag': 'gcr.io/tensorflow/tensorflow:latest',
            'destination': '/home/jovyan/env',
            'source_build_dir': self.build_dir,
            'image_target_name': tag
        }

        # This case fails given the difference in virtualenv path but
        # not sure why.
        problem_args = {
            'ftl_path': '/tmp/tmp7nn4tk7m/ftl.par',
            'virtualenv_path': '/home/jovyan/.conda/envs/dev3/bin/virtualenv',
            'image_base_tag': 'gcr.io/tensorflow/tensorflow:latest',
            'destination': '/home/jovyan/env',
            'source_build_dir': '/tmp/tmp4loe20x1',
            'image_target_name': 'gcr.io/gcrpushtest/test-ship-ftl:0324-1931-dee7'
        },

        # All the deps cases to debug problem with one of these...
        # Could use pytest-cache and separate tests to only re-run failures instead
        # of hacky skip arg

        cases = [
            {
                "skip": True,
                "deps": None,
                "args": base_args
            },
            {
                "skip": True,
                "deps": [
                    "flask"
                ],
                "args": base_args
            },
            {
                "skip": True,
                "deps": [
                    "tensorflow==1.4.1",
                ],
                "args": base_args
            },
            {
                "skip": True,
                "deps": [
                    "kubernetes==5.0.0",
                ],
                "args": base_args
            },
            {
                "skip": True,
                "deps": [
                    # This doesn't, failing with an error about not being
                    # able to access /env. The builds are being run in a container
                    # by a user that does not have root iiuc.
                    "tensor2tensor==1.5.5",
                    # May need to solve this problem by including the code as a
                    # submodule.
                ],
                "args": base_args
            },
            {
                "skip": True,
                "deps": [
                    "allensdk==0.14.4"
                ],
                "args": base_args
            },
            {
                # test a reqs.txt dep via git
                # Fails
                "skip": True,
                "deps": [
                    "-e git://github.com/tensorflow/agents.git@459c4f88ece996eac3489e6e97a6ee0b30bdd6b3#egg=agents"
                ],
                "args": base_args
            },
            {
                "skip": True,
                "deps": [
                    "gym==0.9.4"
                ],
                "args": base_args
            },
            {
                "skip": True,
                "deps": [
                    "google-cloud-storage==1.7.0"
                ],
                "args": base_args
            },
            {
                "skip": False,
                "deps": [
                    "pybullet==1.7.5"
                ],
                "args": base_args
            }
        ]
        
        for case in cases:
            
            if case["skip"]:
                continue
    
            if case["deps"] is not None:
                build_dir = tempfile.mkdtemp()
                with open(os.path.join(build_dir, "requirements.txt"),
                          "w") as f:
                    for dep in case["deps"]:
                        f.write("%s\n" % dep)
            
                case["args"]["source_build_dir"] = build_dir
            logging.info("testing case: %s" % case)
            
            ftl_build_and_push(**case["args"])
        
        
if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    unittest.main()