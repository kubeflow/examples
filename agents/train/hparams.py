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

import multiagent
import tensorflow as tf

import agents
import pybullet


def base():
  """Base hparams tf/Agents PPO."""

  # General
  algorithm = "+agents.ppo.PPOAlgorithm"
  num_agents = 30
  eval_episodes = 30
  use_gpu = False

  # Environment
  env = "AntBulletEnv-v0"
  normalize_ranges = True
  max_length = 1000

  # Network
  network = "+agents.scripts.networks.feed_forward_gaussian"
  weight_summaries = dict(
      all=r'.*', policy=r'.*/policy/.*', value=r'.*/value/.*')
  policy_layers = 200, 100
  value_layers = 200, 100
  init_output_factor = 0.1
  init_logstd = -1
  init_std = 0.35

  # Optimization
  update_every = 60
  update_epochs = 25
  optimizer = "+tf.train.AdamOptimizer"
  learning_rate = 1e-4
  steps = 3e7

  # Losses
  discount = 0.995
  kl_target = 1e-2
  kl_cutoff_factor = 2
  kl_cutoff_coef = 1000
  kl_init_penalty = 1

  return locals()


def hparams_kuka_small():
  pass
