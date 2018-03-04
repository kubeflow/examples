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

"""Provides an entrypoint for the training task."""

from __future__ import absolute_import, division, print_function

import argparse
import datetime
import logging
import os
import pprint
import uuid

import pip
import tensorflow as tf
from google.cloud import storage

import agents

from . import util
from .hparams import base

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


def render(flags):
  """Run a render job."""

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

  gcs_upload_multiple(render_tmp_dir, render_out_dir)


def train(flags):
  """Run a training job."""

  run_config = tf.contrib.learn.RunConfig()

  agents_config = util.get_agents_configuration(
      FLAGS.hparam_set_id, FLAGS.logdir, run_config.is_chief)

  for score in agents.scripts.train.train(agents_config, env_processes=True):
    tf.logging.info('Score {}.'.format(score))


def main(unused_argv):
  """Run training."""

  # By default, log at INFO level
  tf.logging.set_verbosity(tf.logging.INFO)

  # Parse stringified flags from FLAGS.json_flags
  # TODO

  if FLAGS.debug:

    # Enable debug logging
    tf.logging.set_verbosity(tf.logging.DEBUG)

  if FLAGS.run_mode not in ["train", "render"]:
    raise ValueError("Unrecognized run_mode, saw %s" % FLAGS.run_mode)

  if FLAGS.run_mode == 'train':

    # Run in training mode
    train(FLAGS)

  elif FLAGS.run_mode == 'render':

    # Run in render mode
    render(FLAGS)


if __name__ == '__main__':
  tf.app.run()
