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

"""Launcher tests."""

import unittest
import os
import logging
import shutil

from launcher import DownloadJob, InferenceJob, T2TExperiment, T2TDatagenJob, StudyRunnerJob, generate_job_name


def _gen_local_smoke_args():
    
    job_name = generate_job_name("launcher-smoke")
    args = {
        "job_name": job_name,
        "volume_claim_id": "nfs-1",
        "app_root": os.path.realpath(os.path.join(
            os.path.split(__file__)[0], "../")
        ),
        "gcp_project": "foo",
        "namespace": "kubeflow"
    }
    
    return args


def _stage(local_app_root, remote_app_root):
    if not os.path.exists(local_app_root):
        raise ValueError("Can't stage from a non-existent source, "
                         "saw %s" % local_app_root)
    shutil.copytree(local_app_root, remote_app_root)


def _gen_remote_smoke_args():
    
    args = _gen_local_smoke_args()
    local_app_root = args["app_root"]
    
    testing_storage_base = "/mnt/nfs-1/testing"
    remote_app_root = "%s/%s" % (testing_storage_base,
                                 args["job_name"])
    _stage(local_app_root, remote_app_root)
    args["app_root"] = remote_app_root

    return args


class TestDownloadJob(unittest.TestCase):

    def test_smoke_local(self):
        args = _gen_local_smoke_args()
        smoke_job = DownloadJob(**args)
        smoke_job.smoke_local()
    
    def test_smoke_remote(self):
        # Note that this does not yet enforce that a remote job was successful!
        args = _gen_remote_smoke_args()
        smoke_job = DownloadJob(**args)
        smoke_job.smoke_remote()
        
    def test_mini_remote(self):
        
        # A small job that really downloads an image and 
        # generates subimages.
        args = _gen_remote_smoke_args()
        job = DownloadJob(**args)
        job.batch_run(poll_and_check=True)


class TestInferenceJob(unittest.TestCase):
        
    def test_smoke_local(self):
        args = _gen_local_smoke_args()
        smoke_job = InferenceJob(**args)
        smoke_job.smoke_local()
    
    def test_smoke_remote(self):
        args = _gen_remote_smoke_args()
        smoke_job = InferenceJob(**args)
        smoke_job.smoke_remote()


class TestT2TExperiment(unittest.TestCase):
    
    def test_smoke_local(self):
        args = _gen_local_smoke_args()
        args["problem"] = "foo"
        args["hparams_set"] = "foo"
        smoke_job = T2TExperiment(**args)
        smoke_job.smoke_local()
    
    def test_smoke_remote(self):
        args = _gen_remote_smoke_args()
        args["problem"] = "foo"
        args["hparams_set"] = "foo"
        smoke_job = T2TExperiment(**args)
        smoke_job.smoke_remote()


class TestT2TDatagenJob(unittest.TestCase):

    def test_smoke_local(self):
        args = _gen_local_smoke_args()
        args["problem"] = "foo"
        args["tmp_dir"] = "foo"
        smoke_job = T2TDatagenJob(**args)
        smoke_job.smoke_local()
    
    def test_smoke_remote(self):
        args = _gen_remote_smoke_args()
        args["problem"] = "foo"
        args["tmp_dir"] = "foo"
        smoke_job = T2TDatagenJob(**args)
        smoke_job.smoke_remote()


class TestStudyRunnerJob(unittest.TestCase):
        
    def test_smoke_local(self):
        args = _gen_local_smoke_args()
        args["study_id"] = "s1234"
        smoke_job = StudyRunnerJob(**args)
        smoke_job.smoke_local()
    
    def test_smoke_remote(self):
        args = _gen_remote_smoke_args()
        args["study_id"] = "s1234"
        smoke_job = StudyRunnerJob(**args)
        smoke_job.smoke_remote()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    unittest.main()