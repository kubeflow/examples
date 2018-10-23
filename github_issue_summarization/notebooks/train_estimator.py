"""Train using TF Estimator."""
import argparse
import logging
import os
import re
import shutil
import zipfile

def main(args):
  logging.basicConfig(
    level=logging.INFO,
    format=('%(levelname)s|%(asctime)s'
            '|%(pathname)s|%(lineno)d| %(message)s'),
    datefmt='%Y-%m-%dT%H:%M:%S',
  )
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)

  parser = argparse.ArgumentParser()

  parser.add_argument(
    "--model_dir",
    type=str,
    default="Location to save the model.")

  parser.add_argument("--max_steps", type=int, default=2000000)
  parser.add_argument("--eval_steps", type=int, default=1000)

  args = parser.parse_args()

  model_trainer = trainer.Trainer(output_dir)
  model_trainer.preprocess(csv_file, args.sample_size)
  model_trainer.build_model(args.learning_rate)

  local_model_output = args.output_model
  if is_gcs_path(args.output_model):
    local_model_output = os.path.join(output_dir, "model.h5")

  model_trainer.train_keras(local_model_output,
                            base_name=os.path.join(output_dir, "model-checkpoint"),
                            epochs=args.num_epochs)

  # TODO(jlewi): Estimator isn't working so we
  # we should probably train using Keras.
  trainer.train_estimator()

if __name__ == '__main__':
  main()
