# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import logging
import os
import pprint
import subprocess
import tempfile
import uuid

import googleapiclient.discovery
import tensorflow as tf
from google.cloud import storage

import agents


def run_and_output(command, cwd=None, env=None):

  tf.logging.info("Running: %s \ncwd=%s", " ".join(command), cwd)

  if not env:
    env = os.environ
  try:
    output = subprocess.check_output(command, cwd=cwd, env=env,
                                     stderr=subprocess.STDOUT).decode("utf-8")
    tf.logging.info("Subprocess output:\n%s", output)
  except subprocess.CalledProcessError as e:
    tf.logging.info("Subprocess output:\n%s", e.output)
    raise
  return output


def gcs_upload_multiple(local_dir, gcs_out_dir):
  """Upload the contents of a local directory to a specific GCS path.

  Args:
    local_dir (str): The local directory containing files to upload.
    gcs_out_dir (str): The target Google Cloud Storage directory path.

  Raises:
    ValueError: If `gcs_out_dir` does not start with "gs://".

  """

  # Get a list of all files in the local_dir
  local_files = [f for f in os.listdir(
      local_dir) if os.path.isfile(os.path.join(local_dir, f))]
  tf.logging.info("Preparing local files for upload:\n %s" % local_files)

  # Initialize the GCS API client
  storage_client = storage.Client()

  # Raise an error if the target directory cannot be a GCS path
  if not gcs_out_dir.startswith("gs://"):
    raise ValueError(
        "gcs_upload expected gcs_out_dir argument to start with gs://, saw %s" % gcs_out_dir)

  # TODO: Detect and handle case where a GCS path has been provdied
  # corresponding to a bucket that does not exist or for which the user does
  # not have permissions.

  # Obtain the bucket path from the total path
  bucket_path = gcs_out_dir.split('/')[2]
  bucket = storage_client.get_bucket(bucket_path)

  # Construct a target upload path that excludes the initial gs://bucket-name
  blob_base_path = '/'.join(gcs_out_dir.split('/')[3:])

  # For each local file *name* in the list of local file names
  for local_filename in local_files:

    # Construct the target and local *paths*
    blob_path = os.path.join(blob_base_path, local_filename)
    blob = bucket.blob(blob_path)
    local_file_path = os.path.join(local_dir, local_filename)

    # Perform the upload operation
    blob.upload_from_filename(local_file_path)


def _object_import_from_string(name):
  components = name.split('.')
  mod = __import__(components[0])
  for comp in components[1:]:
    mod = getattr(mod, comp)
  return mod


def _realize_import_attrs(d, filter):
  for k, v in d.items():
    if k in filter:
      imported = _object_import_from_string(v)
      # TODO: Provide an appropriately informative error if the import fails
      # except ImportError as e:
      #   msg = ("Failed to realize import path %s." % v)
      #   raise e
      d[k] = imported
  return d


def get_agents_configuration(hparam_set_name, log_dir=None, is_chief=False):
  """Load hyperparameter config."""
  try:
    # Try to resume training.
    hparams = agents.scripts.utility.load_config(log_dir)
  except IOError:

    hparams = hparams_base()

    # --------
    # Experiment extending base hparams with FLAGS and dynamic import of
    # network and algorithm.
    for k, v in FLAGS.__dict__['__flags'].items():
      hparams[k] = v
    hparams = _realize_import_attrs(
        hparams, ["network", "algorithm", "optimizer"])
    # --------

    hparams = agents.tools.AttrDict(hparams)
    hparams = agents.scripts.utility.save_config(hparams, log_dir)

  pprint.pprint(hparams)
  return hparams


def generate_job_name():

  now = datetime.datetime.now()
  name = now.strftime("%m%d-%H%M") + "-" + uuid.uuid4().hex[0:4]
  return name
