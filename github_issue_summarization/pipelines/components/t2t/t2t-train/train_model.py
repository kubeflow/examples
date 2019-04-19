# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""..."""

import argparse
import json
import subprocess


def main():
  parser = argparse.ArgumentParser(description='ML Trainer')
  parser.add_argument(
      '--model-dir',
      help='...',
      required=True)
  parser.add_argument(
      '--data-dir',
      help='...',
      required=True)
  parser.add_argument(
      '--checkpoint-dir',
      help='...',
      required=True)
  parser.add_argument(
      '--train-steps',
      help='...',
      required=True)
  parser.add_argument(
      '--deploy-webapp',
      help='...',
      required=True)

  args = parser.parse_args()

  # Create metadata.json file for visualization.
  metadata = {
    'outputs' : [{
      'type': 'tensorboard',
      'source': args.model_dir,
    }]
  }
  with open('/mlpipeline-ui-metadata.json', 'w') as f:
    json.dump(metadata, f)

  problem = 'gh_problem'
  data_dir = args.data_dir
  print("data dir: %s" % data_dir)
  # copy the model starting point
  model_startpoint = args.checkpoint_dir
  print("model_startpoint: %s" % model_startpoint)
  model_dir = args.model_dir
  print("model_dir: %s" % model_dir)
  model_copy_command = ['gsutil', '-m', 'cp', '-r', model_startpoint, model_dir
      ]
  print(model_copy_command)
  result1 = subprocess.call(model_copy_command)
  print(result1)

  print('training steps (total): %s' % args.train_steps)

  # Then run the training for N steps from there.
  model_train_command = ['t2t-trainer', '--data_dir', data_dir,
     '--t2t_usr_dir', '/ml/ghsumm/trainer',
     '--problem', problem,
     '--model', 'transformer', '--hparams_set', 'transformer_prepend', '--output_dir', model_dir,
     '--job-dir', model_dir,
     '--train_steps', args.train_steps, '--eval_throttle_seconds', '240',
     ]
  print(model_train_command)
  result2 = subprocess.call(model_train_command)
  print(result2)

  # then export the model...

  model_export_command = ['t2t-exporter', '--model', 'transformer',
      '--hparams_set', 'transformer_prepend',
      '--problem', problem,
      '--t2t_usr_dir', '/ml/ghsumm/trainer', '--data_dir', data_dir, '--output_dir', model_dir]
  print(model_export_command)
  result3 = subprocess.call(model_export_command)
  print(result3)

  print("deploy-webapp arg: %s" % args.deploy_webapp)
  with open('/tmp/output', 'w') as f:
    f.write(args.deploy_webapp)

if __name__ == "__main__":
  main()
