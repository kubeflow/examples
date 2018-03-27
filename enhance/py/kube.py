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

"""Kubernetes models and utils supporting templating Job's and TFJob's

TODO: Should consider making use of existing Kubernetes python client object
models, didn't realize these existed.

"""

import datetime
import pprint
import kubernetes
import time
import logging


from util import expect_type, expect_path, object_as_dict, run_and_output, dict_prune_private


# A common base image that extends kubeflow tensorflow_notebook workspace
# image with python dependencies needed for various examples.
# TODO: In the future include various additional deps in this base image
_COMMON_BASE = "gcr.io/kubeflow-rl/common-base:0.0.1"


def gen_timestamped_uid():
    """Generate a timestamped UID of form MMDD-HHMM-UUUU"""
    now = datetime.datetime.now()
    return now.strftime("%m%d-%H%M") + "-" + uuid.uuid4().hex[0:4]


def build_command(base_command, **kwargs):
    """Build a command array extending a base command with -- form kwargs.
    
    E.g. [t2t-trainer, {key: value}] -> [t2t-trainer, --key=value]
    
    """
    expect_type(base_command, str)
    command = [base_command]
    for key, value in kwargs.items():
        expect_type(key, str)
        expect_type(value, str)
        command.append("--%s=%s" % (key, value))
    return command


class AttachedVolume(object):
    """Model of information needed to attach a Kubernetes Volume
    
    Primarily manages correpondence of volume and volume_mount fields and
    expects objects recieving `AttachedVolume` as argument to know whether to
    access `volume` or `volume_mount` fields.
    
    """
    
    def __init__(self, claim_name, mount_path=None, volume_name=None):
        """Define corresponding 
        
        """

        if not isinstance(claim_name, str):
            raise ValueError("Expected string claim_name, saw %s" % claim_name)

        if mount_path is None:
            mount_path = "/mnt/%s" % claim_name
        
        if not isinstance(mount_path, str):
            raise ValueError("Expected string mount_path, saw %s" % claim_name)
        
        if not mount_path.startswith("/"):
            raise ValueError("Mount path should start with '/', saw %s" % mount_path)
    
        if volume_name is None:
            volume_name = claim_name
    
        if not isinstance(volume_name, str):
            raise ValueError("Expected string volume_name, saw %s" % volume_name)
    
        self.volume = {
            "name": volume_name,
            "persistentVolumeClaim": {
                "claimName": claim_name
            }
        }
        self.volume_mount = {
            "name": volume_name,
            "mountPath": mount_path
        }

        
class Resources(object):
    """Model of Kuberentes Container resources"""
    
    def __init__(self, limits=None, requests=None):
        
        allowed_keys = ["cpu", "mem"] #etc...
        
        if limits is not None:
            self.limits = {}
            for key, value in limits.items():
                if key in allowed_keys:
                    self.limits[key] = value
        
        if requests is not None:
            self.requests = {}
            for key, value in requests.items():
                if key in allowed_keys:
                    self.requests[key] = value


class Container(object):
    """Model of Kubernetes Container object."""
    
    def __init__(self, args, image, name, resources=None, attached_volume=None):
        self.args = args
        self.image = image
        self.name = name
        
        if resources is not None:
            if not isinstance(resources, Resources):
                raise ValueError("non-null resources expected to be of "
                                 "type Resources, saw %s" % type(resources))
            self.resources = resources
        
        if attached_volume is not None:
            if not isinstance(attached_volume, AttachedVolume):
                raise ValueError("non-null attached_volume expected to be of "
                                 "type AttachedVolume, saw %s" % type(attached_volume))
            self.volumeMounts = [attached_volume.volume_mount]


class TFJobReplica(object):
    """Python model of a kubeflow.org TFJobReplica object."""
    
    def __init__(self, replica_type, num_replicas, args, image,
                 resources=None, attached_volume=None, restart_policy="OnFailure"):
        
        self.replicas = num_replicas
        
        self.template = {
            "spec": {
                "containers": [
                    Container(args, image, "tensorflow",
                              resources, attached_volume)
                ],
                "restartPolict": restart_policy,
            }
        }

        self.tfReplicaType = replica_type
                
        if isinstance(attached_volume, AttachedVolume):
            # Add attached volume to repliac spec
            self.template["spec"]["volumes"] = [
                attached_volume.volume
            ]


class TFJob(object):
    """Python model of a kubeflow.org TFJob object"""
    
    def __init__(self, name, namespace, replicas):
        # Camel case to be able to conveniently display in kube-compatible
        # version with self.__dict__
        self.apiVersion = "kubeflow.org/v1alpha1"
        self.kind = "TFJob"
        self.metadata = {
            "name": name,
            "namespace": namespace
        }
        self.spec = {"replicaSpecs": []}
        for replica in replicas:
            self.spec["replicaSpecs"].append(replica.__dict__)
    
    def run(self, crd_client, show=True):
        job_dict = object_as_dict(self)
        logging.info("Running TFJob with name %s..." % job_dict["metadata"]["name"])
        return crd_client.create_namespaced_custom_object("kubeflow.org", "v1alpha1",
                                                          job_dict["metadata"]["namespace"],
                                                          "tfjobs", body=job_dict)


def status_callback(job_response):
    """A callback to use with wait_for_job."""
    logging.info("Job %s in namespace %s; uid=%s; succeeded=%s" % (
        job_response.metadata.name,
        job_response.metadata.namespace,
        job_response.metadata.uid,
        job_response.status.succeeded
    ))


# TODO: This defines success as there having been exactly one success.
def wait_for_job(batch_api,
                 namespace,
                 name,
                 timeout=datetime.timedelta(seconds=(5*60)),
                 polling_interval=datetime.timedelta(seconds=5)):
    # ported from https://github.com/kubeflow/tf-operator/blob/master/py/tf_job_client.py
    end_time = datetime.datetime.now() + timeout
    while True:
        response = batch_api.read_namespaced_job_status(name, namespace)

        if status_callback:
            status_callback(response)
    
        if response.status.succeeded == 1:
            return response

        if datetime.datetime.now() + polling_interval > end_time:
            raise TimeoutError(
                "Timeout waiting for job {0} in namespace {1} to finish.".format(
                name, namespace))

        time.sleep(polling_interval.seconds)

    # Linter complains if we don't have a return statement even though
    # this code is unreachable.
    return None


#TODO: Consider pip installing additional dependencies on job startup
class Job(object):
    """Python model of a Kubernetes Job object."""
    
    def __init__(self, job_name, command,
                 image=_COMMON_BASE,
                 restart_policy="Never",
                 namespace="default",
                 volume_claim_id=None,
                 batch=True,
                 no_wait=False,
                 *args, **kwargs):
        """Check args for and template a Job object.
        
        name (str): A unique string name for the job.
        image (str): The image within which to run the job command.
        restart_policy (str): The restart policy (e.g. Never, onFailure).
        namespace (str): The namespace within which to run the Job.
        volume_claim_id (str): The ID of a persistent volume to mount at
            /mnt/`volume_claim_id`.

        See: https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/
        
        """
        
        # Private attributes will be ignored when converting object to dict.
        self._command = command
        self._batch = batch
        self._poll_and_check = True
        if no_wait:
            self._poll_and_check = False
        
        kwargs = {
            "args": command,
            "image": image,
            "name": "container",
            "resources": None,
            "attached_volume": None
        }

        attached_volume = None
        if volume_claim_id is not None:
            attached_volume = AttachedVolume(volume_claim_id)
            kwargs["attached_volume"] = attached_volume
        
        container = Container(**kwargs)
            
        self.apiVersion = "batch/v1"
        self.kind = "Job"
        self.metadata = {
            "name": job_name,
            "namespace": namespace
        }
        self.spec = {
            "template": {
                "spec": {
                    "containers": [container],
                    "restartPolicy": restart_policy
                }
            },
            "backoffLimit": 4
        }
        
        if attached_volume is not None:
            self.spec["template"]["spec"]["volumes"] = [
                attached_volume.volume
            ]
          
    def run(self, show=True):
        
        if self._batch:
            self.batch_run(poll_and_check=self._poll_and_check)
        else:
            self.local_run()
            
    def as_dict(self):
        return dict_prune_private(object_as_dict(self))

    def batch_run(self, poll_and_check=False):
        
        kubernetes.config.load_kube_config()
        
        job_client = kubernetes.client.BatchV1Api()

        job_dict = self.as_dict()
        
        response = job_client.create_namespaced_job(
            job_dict["metadata"]["namespace"],
            job_dict
        )
        
        pprint.pprint(response)
        
        if poll_and_check:
            # Poll for job completion and check status, raising exception
            # if not successful
            # TODO
            wait_for_job(job_client,
                         job_dict["metadata"]["namespace"],
                         job_dict["metadata"]["name"])
            
    def local_run(self, show=True):
        """Run the job command locally."""
        output = run_and_output(self._command)
    
    def smoke_local(self):
        """Append --help to command and run locally."""
        self._command.append("--help")
        self.local_run()
        
    def smoke_remote(self):
        self._command.append("--help")
        self.batch_run(poll_and_check=True)
        # Note that this does not yet enforce that a remote job was successful