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

"""Tools supporting various means of shipping workspaces."""

import os
import datetime
import uuid
from util import expect_path, run_and_output
import yaml
import logging
import shutil
import tempfile


def stage_workspace(train_dir, workspace_root):
    workspace_mount_path = os.path.join(train_dir, "workspace")
    if os.path.exists(workspace_mount_path):
        logging.info("Staged workspace already exists, skipping creation for path: %s" % workspace_mount_path)
    shutil.copytree(workspace_root, workspace_mount_path)
    logging.info("Successfully staged workspace to %s" % workspace_mount_path)
    return workspace_mount_path


def generate_image_tag(project_or_user, app_name, registry_target="gcr.io"):
    """Tags of format {registry_target}/{project_or_user}/{app_name}:{uid}"""
    now = datetime.datetime.now()
    build_id = now.strftime("%m%d-%H%M") + "-" + uuid.uuid4().hex[0:4]
    return "%s/%s/%s:%s" % (registry_target, project_or_user, app_name, build_id)


def gcb_build_and_push(image_tag, build_dir,
                       cache_from="tensorflow/tensorflow:1.4.1",
                       dry_run=False):
    """Generate GCB config and build container, caching from `cache_from`.
    
    A Google Container Builder build.yaml config will be produced in `build_dir`
    and if not `dry_run` a system call will be made from `build_dir` to
    'gcloud container build submit --config build.yaml .'.
    
    Args:
        image_tag (str): The tag to apply to the newly built image.
        build_dir (str): Path to directory to use as '.' during GCB build.
        cache_from (str): A container image string identifier.
        dry_run (bool): Whether to actually trigger the build on GCB.

    TODO: Use GCB REST API.
    
    """
    expect_path(build_dir)
    os.chdir(build_dir)
        
    build_config = {
        "steps": [
            {
                "name": "gcr.io/cloud-builders/docker",
                "args": [
                    "pull", cache_from
                ]
            },
            {
                "name": "gcr.io/cloud-builders/docker",
                "args": [
                    "build",
                    "--cache-from",
                    cache_from,
                    "-t", image_tag,
                    "."
                ]
            }
        ],
        "images": [image_tag]
    }
    output_config_path = "build.yaml"
    if build_dir is not None:
        output_config_path = os.path.join(build_dir, output_config_path)
    with open("build.yaml", "w") as f:
        f.write(yaml.dump(build_config))

    build_config = os.path.join(build_dir, "build.yaml")
    logging.info("Generated build config: %s" % build_config)
    
    output = None
    if not dry_run:
        logging.info("Triggering build...")
        os.chdir(build_dir)
        output = run_and_output(["gcloud", "container", "builds", "submit",
                                 "--config", "build.yaml", "."])
    
    return build_config


def fetch_ftl():
    """Download the FTL par file.
    
    Returns:
        str: The path to the obtained ftl.par file.
        
    """
    ftl_url = ("https://storage.googleapis.com/"
               "gcp-container-tools/ftl/python/"
               "latest/ftl.par")
    
    ftl_dir = tempfile.mkdtemp()
    os.chdir(ftl_dir)
    run_and_output(["wget", ftl_url])
    ftl_path = os.path.join(ftl_dir, "ftl.par")
    if not os.path.exists(ftl_path):
        logging.error("Failed to obtain FTL.")
        raise

    return ftl_path


def try_lookup_venv_command():
    """Try looking up the virtualenv command path."""
    
    output = run_and_output(["which", "virtualenv"]).strip()
    
    if len(output) == 0:
        raise ValueError("Couldn't find a virtualenv binary in current env.")
    
    logging.info("Found virtualenv command at path: %s" % output)
    
    return output


def ftl_build_and_push(image_target_name, source_build_dir,
                       destination,
                       image_base_tag, virtualenv_path=None,
                       ftl_path=None):
    """Use FTL to build and push a container image.
    
    Args:
        image_target_name (str): The full image identifier string for the resulting
            image (e.g. gcr.io/project/name:tag)
        source_build_dir (str): The directory containing a requirements.txt file
            to use as the build directory which will result in those requirements
            being installed and the contents of that directory being staged to
            container /srv or an alternative path specified by --directory.
        image_base_tag (str): The full image identifier string for the image on
            on which the build should be based (i.e. the analog of what is
            specified via FROM {base_name} in a Dockerfile).
        virtualenv_path (str): The string path to a virtualenv executable.
        ftl_path (str): The string path to an ftl.par executable.
    
    """
    
    logging.info("calling build and push with args: %s" % locals())
    
    if ftl_path is None:
        ftl_path = fetch_ftl()
    
    if virtualenv_path is None:
        virtualenv_path = try_lookup_venv_command()
        
    cmd = ["python2", ftl_path,
             "--virtualenv-cmd", virtualenv_path,
             "--cache",
             "--name", image_target_name,
             "--directory", source_build_dir,
             "--base", image_base_tag,
             "--destination", destination]
    
    logging.info("calling command: %s" % " ".join(cmd))
    output = run_and_output(cmd)
    return output