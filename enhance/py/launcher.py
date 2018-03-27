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

"""Experiment """

from kube import Job
import argparse
import logging
import pprint
import datetime
import uuid
from util import object_as_dict, maybe_mkdir
from ship import gcb_build_and_push, generate_image_tag
import shutil
import os

_APP_NAME = "enhance"

def generate_job_name(app_name):
    """Generate a unique job name from a study ID."""
    
    now = datetime.datetime.now()
    job_id = now.strftime("%m%d-%H%M") + "-" + uuid.uuid4().hex[0:4]
    job_name = "%s-%s" % (app_name, job_id)
    job_name = job_name.replace("_", "-")
    
    return job_name


class DownloadJob(Job):
    """A Job that runs the data downloader."""
    
    def __init__(self, app_root, *args, **kwargs):
        
        data_root = os.path.join(app_root, "data")
        
        command = [
            "python", "%s/py/download.py" % app_root,
            "--data_root", data_root
        ]
        
        super(DownloadJob, self).__init__(command=command,
                                          *args, **kwargs)

        
class T2TDatagenJob(Job):
    """A Job that generates training examples from raw input data."""
    
    # TODO: Mixing up data_dir and tmp_dir...
    
    def __init__(self, app_root, problem, tmp_dir, *args, **kwargs):
        
        command = [
            "t2t-datagen",
            "--t2t_usr_dir", "%s/py" % app_root,
            "--problem", problem,
            "--tmp_dir", tmp_dir
        ]
        
        super(T2TDatagenJob, self).__init__(command=command,
                                            *args, **kwargs)


# So this obvi should be a TFJob
class T2TExperiment(Job):
    """A Job that trains a model within the tensor2tensor framework."""
    
    def __init__(self, problem, hparams_set, app_root, *args, **kwargs):
        
        # Construct a command that when run will 
        command = [
            "t2t-trainer",
            "--t2t_usr_dir", "%s/py" % app_root,
            "--problem", problem,
            "--hparams_set", hparams_set
        ]
        
        super(T2TExperiment, self).__init__(command=command,
                                            *args, **kwargs)

        
class InferenceJob(Job):
    """A Job that infers outputs from inputs given a parameterized model."""
    
    def __init__(self, app_root, *args, **kwargs):
        
        command = [
            "t2t-decoder",
            "--t2t_usr_dir", "%s/py" % app_root
        ]
        
        super(InferenceJob, self).__init__(command=command,
                                           *args, **kwargs)


class StudyRunnerJob(Job):
    """A Job that runs a Study, searching for optimal model parameters."""

    def __init__(self, study_id, app_root, *args, **kwargs):
    
        command = ["python", "%s/py/study.py" % app_root,
                   "--study_id", study_id]
        
        super(StudyRunnerJob, self).__init__(command=command,
                                             *args, **kwargs)

        
# Modes in which the launcher can be run along with their added arg templates
launcher_modes = {
    "download": {
        "job_object": DownloadJob,
        "arg_template": []
    },
    "inference": {
        "job_object": InferenceJob,
        "arg_template": [
            
        ]
    },
    "train": {
        "job_object": T2TExperiment,
        "arg_template": [
            {
                "name": "problem"
            },
            {
                "name": "hparams_set"
            }
        ],
    },
    "datagen": {
        "job_object": T2TDatagenJob,
        "arg_template": [
            {
                "name": "problem",
                "required": True
            },
            {
                "name": "tmp_dir",
                "required": True
            }
        ],
    },
    "study_runner": {
        "job_object": StudyRunnerJob,
        "arg_template": [
            {
                "name": "study_id",
                "required": True
            }
        ],
    }
}


# TODO: Not my fave, this and the above needs to be integreated with main functions of
# individual steps and maybe use tf.app.flags.
def extend_parser(parser, extra_args):
    
    for item in extra_args:
        if "name" not in item:
            raise ValueError("Every arg template item should have a name attribute.")
        
        help_text = ""
        req = False
        if "help" in item:
            help_text = item["help"]
        if "required" in item:
            req = item["required"]
        parser.add_argument("--%s" % item["name"], help=help_text, required=req)            
    
    return parser


if __name__ == "__main__":
    
    """This works but is slow and does not stream build output."""
    
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--gcp_project", dest="gcp_project",
                        help="The name of a GCP project.")
    parser.add_argument("--app_root", dest="app_root",
                        help="The root FS path to the enhance app.")
    parser.add_argument("--image", dest="use_image",
                        default="gcr.io/kubeflow-rl/common-base:0.0.1",
                        help=("The name of a container image to use for the "
                              "training job (instead of building a new one.)"))
    parser.add_argument("--batch", action="store_true",
                        help=("Whether to launch a batch or local run, defaulting "
                              "to running locally."))
    parser.add_argument("--rebuild_base", action="store_true",
                        help=("Whether to re-build the base image such as when "
                              "updating depenencies."))
    parser.add_argument("--volume_claim_id", dest="volume_claim_id",
                        default="nfs-1",
                        help="The volume claim ID for shared storage.")
    parser.add_argument("--no-wait", dest="no_wait",
                        action="store_true",
                        help=("Whether to skip polling for job completion and "
                              "return immediately."))
    parser.add_argument("--namespace", dest="namespace",
                        default="kubeflow",
                        help="The namespace in which to run the job.")
    parser.add_argument("--mode", dest="mode",
                        default=None,
                        help=("The mode in which to run, one of "
                              "%s." % launcher_modes.keys()))
    
    args, _ = parser.parse_known_args()

    if args.mode not in launcher_modes:
        raise ValueError("Unrecognized run mode, mode specified via --mode "
                         "must be one of %s." % launcher_modes.keys())

    parser = extend_parser(parser, launcher_modes[args.mode]["arg_template"])
    
    # Now with all of them
    args, _ = parser.parse_known_args()
    
    logging.info("Parsed args: %s" % args.__dict__)

    if args.app_root is None:
        raise ValueError("Please specify an app root via --app_root.")
        
    
    args.job_name = generate_job_name("enhance")
    
    # Construct the NFS root path from the volume_claim_id
    nfs_root = "/mnt/%s" % args.volume_claim_id
    
    # Construct a path into which to write training logs and stage the workspace
    args.study_root = "%s/studies/dev/%s" % (nfs_root, args.job_name)
    
    staging_path = os.path.join(args.study_root, "staging")
           
    # For now we're using the following FS structure for a study:
    # {study_root}/
    #   staging/
    #       ...
    #       py/
    #       ...
    #   job_1_logdir/
    #   job_2_logdir/
    #   ...
    
    # Expect to find trainer code at staged path, i.e. /mnt/nfs-1/...
    os.makedirs(args.study_root, exist_ok=True)
    shutil.copytree(args.app_root, staging_path)
    logging.info("Staged app workdir to %s" % staging_path)
    
    if args.batch:
        # If running in batch, args.app_root needs to be modified before being passed
        # into the job object because this argument will refer to the runtime app root,
        # not the app root at launch time.
        args.app_root = staging_path

    if args.rebuild_base:
                
        if args.gcp_project is None:
            raise ValueError("If --rebuild_base both --app_root "
                             "and --gcp_project are required as a new image "
                             "will be built from `app_root`.")
        args.image = generate_image_tag(args.gcp_project, _APP_NAME)
        gcb_build_and_push(args.image, staging_path)
            
    job = launcher_modes[args.mode]["job_object"](**args.__dict__)
    
    pprint.pprint(object_as_dict(job))
    
    job.run()
