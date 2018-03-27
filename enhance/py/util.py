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

"""General utilities."""

import os
import subprocess
import shutil
import argparse
import logging
import datetime
import uuid


def run_and_output(command, cwd=None, env=None):
    """Run a system command.
    
    Args:
        command (list): The command to run as a string array.
        cwd (str): The directory to set as the current working directory
        env (list): Variables to make available in environment of command
    
    Returns:
        str: A string storing the stdout produced by running the command.
        
    Raises:
        CalledProcessError: If the command run exits with a system error.
    
    """

    logging.info("Running: %s \ncwd=%s", " ".join(command), cwd)

    if not env:
        env = os.environ
    try:
        output = subprocess.check_output(command, cwd=cwd, env=env,
                                         stderr=subprocess.STDOUT).decode("utf-8")
        logging.info("Subprocess output:\n%s", output)
    except subprocess.CalledProcessError as e:
        logging.info("Command failed, subprocess output:\n%s", e.output)
        raise
    return output


def _gcloud_pull_kube_credentials(global_config):
    command = "gcloud container clusters --project=%s --zone=%s get-credentials %s" % (
        global_config["project"], global_config["zone"], global_config["cluster"]
    )
    return run_and_output(command.split(" "))


def _create_namespace(namespace):
    """Create a kubernetes namespace if it does not already exist.
    
    This function first checks to see if the given namespace already exists.
    If not, it is created through a `kubectl` system call.
    
    Args:
        namespace (str): The name of the namespace to create.
    
    """
    namespaces = run_and_output(["kubectl", "get", "namespaces",
                                       "-o", "jsonpath='{.items[*].metadata.name}'"]).split(" ")
    if namespace in namespaces:
        logging.info("namespace %s already exists, skipping creation." % namespace)
        return
    run_and_output(["kubectl", "create", "namespace", namespace])  

    
def _ks_register_kube_config(ks_app_root):
    """Register current kubernetes config. as a ksonnet environment.
    
    This function changes to root directory of a ksonnet app and
    attempts to add/create a new default environment referencing the 
    current Kubernetes config. If this fails, it attempts to set
    (instead of create) the default environment.
    
    See also: https://ksonnet.io/docs/concepts
    
    Args:
        workspace_root (str): The root path to a Ksonnet workspace.
    
    """
    os.chdir(ks_app_root)
    try:
        run_and_output(["ks", "env", "add", "default"])
    except subprocess.CalledProcessError as e:
        run_and_output(["ks", "env", "set", "default"])

            
def setup_workspace(workspace_root, app_name, nfs_root, project, zone, cluster, nfs_claim_id, namespace):
    
    global_config = {
        "workspace_root": workspace_root,
        "app_name": app_name,
        "nfs_root": nfs_root,
        "project": project,
        "zone": zone,
        "cluster": cluster,
        "nfs_claim_id": nfs_claim_id,
        "namespace": namespace
    }
    
    # TODO: We may want to just assume nfs_root is /mnt/{nfs_claim_id}.
       
    app_root = os.path.join(workspace_root,
                            app_name)
    
    global_config["app_root"] = app_root
    
    expect_paths(["app_root", "nfs_root"], global_config)

    # Implicitly verifies that the specified project is accessible and provided zone
    # correspond to provided cluster name
    # In the future this can be made provider-agnostic by sharing kube credentials via a kube secret
    # or creating secondary API
    _gcloud_pull_kube_credentials(global_config)
    
    _create_namespace(global_config)
    
    _ks_setup_workspace(global_config)
    
    logging.info("global config: %s" % global_config)
        
    return global_config
        
        
def launch_tensorboard(train_job_name, train_log_path, namespace, global_config):
    """Launch tensorboard."""
    
    #TODO: Enforce train job name starts with letter?
        
    job_config = {
        "log_dir": train_log_path,
        "name": train_job_name,
        "namespace": namespace
    }
    
    os.chdir(os.path.join(global_config["app_root"], "app")) 
    
    for key, value in job_config.items():
        run_and_output(["ks", "param", "set", "tensorboard", key, str(value)])
    
    run_and_output(["ks", "apply", "default", "-c", "tensorboard"])

    port=8001
    url=("http://127.0.0.1:{port}/api/v1/proxy/namespaces/{namespace}/services/{service_name}:80/".format(
        port=port, namespace=namespace, service_name=(train_job_name+"-tb")))

    return "You can access tensorboard from your local machine via the following URL: %s" % url


def stage_workspace(train_dir, workspace_root):
    workspace_mount_path = os.path.join(train_dir, "workspace")
    if os.path.exists(workspace_mount_path):
        logging.info("Staged workspace already exists, skipping creation for path: %s" % workspace_mount_path)
    shutil.copytree(workspace_root, workspace_mount_path)
    logging.info("Successfully staged workspace to %s" % workspace_mount_path)
    return workspace_mount_path


def launch_training_job(problem, model, hparam_id, data_root, app_name, namespace, nfs_root,
          workspace_root, app_root, num_cpu=1, num_replicas=1, train_steps=100,
          eval_steps=10, dry_run=False, **kwargs):
    """Train the image enhancement model."""
    
    job_config = {
        "problem": problem,
        "model": model,
        "hparam_id": hparam_id,
        "data_root": data_root,
        "train_steps": train_steps,
        "t2t_command": "t2t-trainer",
        "app_name": app_name,
        "namespace": namespace
    }
    
    now = datetime.datetime.now()
    job_id = now.strftime("%m%d-%H%M") + "-" + uuid.uuid4().hex[0:4]
    job_name = "%s-%s" % (problem, job_id)
    job_name = job_name.replace("_", "-")
    job_config["job_name"] = job_name
        
    # Construct train dir path
    train_dir_base = "%s/train_dirs/%s/%s-%s" % (nfs_root,
                                                 problem,
                                                 model,
                                                 hparam_id)
    train_dir = os.path.join(train_dir_base, job_id)
    os.makedirs(train_dir, exist_ok=True)
    job_config["train_dir"] = train_dir

    workspace_mount_path = stage_workspace(train_dir, workspace_root)
    staging_python_root = os.path.join(workspace_mount_path, app_name, "py")
    job_config["staging_python_root"] = staging_python_root
    
    expect_paths(["staging_python_root", "train_dir", "data_root"], job_config)
    
    # Configure the job startup command
    logging.info(staging_python_root)
    logging.info(os.listdir(staging_python_root))
    
    os.chdir(os.path.join(app_root, "app")) 
    
    #for key, value in job_config.items():
    #    run_and_output(["ks", "param", "set", "train", key, str(value)])
    
    #tf.logging.info("job config: %s" % job_config)
    
    #if not dry_run:
        # Run the job
    #    run_and_output(["ks", "apply", "default", "-c", "train"])
         
    return job_config


def object_as_dict(obj):
    if hasattr(obj, "__dict__"):
        obj = obj.__dict__
    if isinstance(obj, dict):
        data = {}
        for key, value in obj.items():
            data[key] = object_as_dict(value)
        return data
    elif isinstance(obj, list):
        return [object_as_dict(item) for item in obj]
    else:
        return obj

def show_object(obj):
    pp = pprint.PrettyPrinter(indent=0)
    pp.pprint(object_as_dict(obj))

def object_as_yaml(obj):
    d = object_as_dict(obj)
    return yaml.dump(d, default_flow_style=False)

def expect_path(path):
    """Check that a path exists (and is a valid).
    
    Args:
        path (str): An absolute, user-space path (e.g. /mnt/nfs/foo).
    
    Raises:
        ValueError: If the path is not a string that starts with '/' referring
            to extant path.
        
    """
    if not isinstance(path, str):
        raise ValueError("Paths must be of type string, saw: %s" % path)
    if not path.startswith("/"):
        raise ValueError("Expected an absolute, user-space path, saw: %s" % path)
    if not os.path.exists(path):
        raise ValueEror("Path does not exist: %s" % path)

def expect_type(obj, ty):
    """Check that `obj` is of type `ty`.
    
    Raises:
        ValueError: If `obj` is not of type `ty`.
        
    """
    if not isinstance(obj, ty):
        raise ValueError("Expected type %s, saw object %s of type %s" % (ty, obj, type(obj)))

def gen_timestamped_uid():
    """Generate a string uid of the form MMDD-HHMM-UUUU."""
    now = datetime.datetime.now()
    return now.strftime("%m%d-%H%M") + "-" + uuid.uuid4().hex[0:4]

def maybe_mkdir(path):
    """Single interface to multiple ways of mkdir -p.
    
    Looks like os.makedirs(..., exist_ok=True) doesn't work with
    python 2.7. Changing interface once.
    
    """
    return run_and_output(["mkdir", "-p", path])


def dict_prune_private(d):
    """Return a copy of a dict removing subtrees with keys starting with '_'."""
    
    if isinstance(d, dict):
        data = {}
        for key, value in d.items():
            if not key.startswith("_"):
                data[key] = dict_prune_private(value)
        return data
    else:
        return d
