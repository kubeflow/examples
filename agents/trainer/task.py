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

"""Provides an entrypoint for the training and rendering tasks.

Usage: python -m trainer.task [options]

"""

from __future__ import absolute_import, division, print_function

import datetime
import logging
import os
import pprint
import uuid
import shutil

from google.cloud import storage
import tensorflow as tf

#pylint: disable=unused-import
import pybullet_envs

import agents


flags = tf.app.flags

flags.DEFINE_string("run_mode", "train",
                    "Run mode, one of [train, render, train_and_render].")
flags.DEFINE_string("logdir", '/tmp/test',
                    "The base directory in which to write logs and "
                    "checkpoints.")
flags.DEFINE_string("hparam_set_id", "pybullet_kuka_ff",
                    "The name of the config object to be used to parameterize "
                    "the run.")
flags.DEFINE_string("run_base_tag",
                    datetime.datetime.now().strftime('%Y%m%dT%H%M%S'),
                    "Base tag to prepend to logs dir folder name. Defaults "
                    "to timestamp.")
flags.DEFINE_boolean("env_processes", True,
                     "Step environments in separate processes to circumvent "
                     "the GIL.")
flags.DEFINE_integer("num_gpus", 0,
                     "Total number of gpus for each machine."
                     "If you don't use GPU, please set it to '0'")
flags.DEFINE_integer("save_checkpoint_secs", 600,
                     "Number of seconds between checkpoint save.")
flags.DEFINE_boolean("log_device_placement", False,
                     "Whether to output logs listing the devices on which "
                     "variables are placed.")
flags.DEFINE_boolean("debug", True,
                     "Run in debug mode.")

# Render
flags.DEFINE_integer("render_secs", 600,
                     "Number of seconds between triggering render jobs.")
flags.DEFINE_string("render_out_dir", None,
                    "The path to which to copy generated renders.")

# Algorithm
flags.DEFINE_string("algorithm", "agents.ppo.PPOAlgorithm",
                    "The name of the algorithm to use.")
flags.DEFINE_integer("num_agents", 30,
                     "The number of agents to use.")
flags.DEFINE_integer("eval_episodes", 25,
                     "The number of eval episodes to use.")
flags.DEFINE_string("env", "AntBulletEnv-v0",
                    "The gym / bullet simulation environment to use.")
flags.DEFINE_integer("max_length", 1000,
                     "The maximum length of an episode.")
flags.DEFINE_integer("steps", 10000000,
                     "The number of steps.")

# Network
flags.DEFINE_string("network", "agents.scripts.networks.feed_forward_gaussian",
                    "The registered network name to use for policy and value.")
flags.DEFINE_float("init_mean_factor", 0.1,
                   "")
flags.DEFINE_float("init_std", 0.35,
                   "")

# Optimization
flags.DEFINE_float("learning_rate", 1e-4,
                   "The learning rate of the optimizer.")
flags.DEFINE_string("optimizer", "tensorflow.train.AdamOptimizer",
                    "The import path of the optimizer to use.")
flags.DEFINE_integer("update_epochs", 25,
                     "The number of update epochs.")
flags.DEFINE_integer("update_every", 60,
                     "The update frequency.")

# Losses
flags.DEFINE_float("discount", 0.995,
                   "The discount.")
flags.DEFINE_float("kl_target", 1e-2,
                   "the KL target.")
flags.DEFINE_integer("kl_cutoff_factor", 2,
                     "The KL cutoff factor.")
flags.DEFINE_integer("kl_cutoff_coef", 1000,
                     "The KL cutoff coefficient.")
flags.DEFINE_integer("kl_init_penalty", 1,
                     "The initial KL penalty?.")

FLAGS = flags.FLAGS


hparams_base = {

  # General
  "algorithm": agents.ppo.PPOAlgorithm,
  "num_agents": 30,
  "eval_episodes": 30,
  "use_gpu": False,

  # Environment
  "env": 'KukaBulletEnv-v0',
  "normalize_ranges": True,
  "max_length": 1000,

  # Network
  "network": agents.scripts.networks.feed_forward_gaussian,
  "weight_summaries": dict(
    all=r'.*', policy=r'.*/policy/.*', value=r'.*/value/.*'),
  "policy_layers": (200, 100),
  "value_layers": (200, 100),
  "init_output_factor": 0.1,
  "init_logstd": -1,
  "init_std": 0.35,

  # Optimization
  "update_every": 60,
  "update_epochs": 25,
  "optimizer": tf.train.AdamOptimizer,
  "learning_rate": 1e-4,
  "steps": 3e7,  # 30M

  # Losses
  "discount": 0.995,
  "kl_target": 1e-2,
  "kl_cutoff_factor": 2,
  "kl_cutoff_coef": 1000,
  "kl_init_penalty": 1,
}


def _object_import_from_string(name):
  """Import and return an object from a string import path.

  Args:
    name (str): A string import path
        (e.g. "tf.train.AdamOptimizer")

  Returns:
    obj: The imported Python object

  """
  components = name.split('.')
  mod = __import__(components[0])
  for comp in components[1:]:
    mod = getattr(mod, comp)
  return mod


def _realize_import_attrs(d, hparam_filter):
  """Import objects from string paths in dict if in `hparam_filter`.

  Notes:
  The following call with an optimizer object referenced as a str:
      _realize_import_attrs(
          {"optimizer":"tf.train.AdamOptimizer"},
          ["optimizer"])
  returns {"optimizer": tf.train.AdamOptimizer}

  This is part of an experiment on how to make all hyperparameters
  configurable, including python objects, towards more flexible
  tuning.

  """
  for k, v in d.items():
    if k in hparam_filter:
      imported = _object_import_from_string(v)
      # TODO: Provide an appropriately informative error if the import fails
      # except ImportError as e:
      #   msg = ("Failed to realize import path %s." % v)
      #   raise e
      d[k] = imported
  return d


def _get_agents_configuration(log_dir=None):
  """Load hyperparameter config.

  Args:
    log_dir (str): The directory in which to search for a
        tensorflow/agents config file.

  Returns:
    dict: A dictionary storing the hyperparameter config.
        for this run.

  """
  try:
    # Try to resume training.
    hparams = agents.scripts.utility.load_config(log_dir)
  except IOError:

    hparams = hparams_base

    # --------
    # Experimental
    for k, v in FLAGS.__dict__['__flags'].items():
      hparams[k] = v
    hparams = _realize_import_attrs(
        hparams, ["network", "algorithm", "optimizer"])
    # --------

    hparams = agents.tools.AttrDict(hparams)
    hparams = agents.scripts.utility.save_config(hparams, log_dir)

  pprint.pprint(hparams)
  return hparams


def gcs_upload(local_dir, gcs_out_dir):
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


def main(_):
  """Configures run and initiates either training or rendering."""

  tf.logging.set_verbosity(tf.logging.INFO)

  if FLAGS.debug:
    tf.logging.set_verbosity(tf.logging.DEBUG)

  log_dir = FLAGS.logdir

  agents_config = _get_agents_configuration(log_dir)

  if FLAGS.run_mode == 'train':
    for score in agents.scripts.train.train(agents_config, env_processes=True):
      logging.info('Score %s.', score)
  if FLAGS.run_mode == 'render':
    now = datetime.datetime.now()
    subdir = now.strftime("%m%d-%H%M") + "-" + uuid.uuid4().hex[0:4]
    render_tmp_dir = "/tmp/agents-render/"
    os.system('mkdir -p %s' % render_tmp_dir)
    agents.scripts.visualize.visualize(
        logdir=FLAGS.logdir, outdir=render_tmp_dir, num_agents=1, num_episodes=1,
        checkpoint=None, env_processes=True)
    render_out_dir = FLAGS.render_out_dir
    # Unless a render out dir is specified explicitly upload to a unique subdir
    # of the log dir with the parent render/
    if render_out_dir is None:
      render_out_dir = os.path.join(FLAGS.logdir, "render", subdir)
    if render_out_dir.startswith("gs://"):
      gcs_upload(render_tmp_dir, render_out_dir)
    else:
      shutil.copytree(render_tmp_dir, render_out_dir)

  return True


if __name__ == '__main__':
  tf.app.run()
