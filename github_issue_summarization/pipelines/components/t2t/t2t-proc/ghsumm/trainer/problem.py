import csv

import os
import tensorflow as tf
from tensor2tensor.utils import registry
from tensor2tensor.models import transformer
from tensor2tensor.data_generators import problem
# from tensor2tensor.data_generators import text_encoder
from tensor2tensor.data_generators import text_problems
# from tensor2tensor.data_generators import generator_utils

from tensorflow.python.lib.io import file_io


@registry.register_problem
class GhProblem(text_problems.Text2TextProblem):
  """... predict GH issue title from body..."""

  @property
  def approx_vocab_size(self):
    return 2**13  # ~8k

  @property
  def is_generate_per_split(self):
    # generate_data will NOT shard the data into TRAIN and EVAL for us.
    return False

  @property
  def max_subtoken_length(self):
    return 4

  @property
  def dataset_splits(self):
    """Splits of data to produce and number of output shards for each."""
    # 10% evaluation data
    return [{
        "split": problem.DatasetSplit.TRAIN,
        "shards": 90,
    }, {
        "split": problem.DatasetSplit.EVAL,
        "shards": 10,
    }]

  def generate_samples(self, data_dir, tmp_dir, dataset_split):
    with open('/ml/gh_data/github_issues.csv') as csvfile:
      ireader = csv.reader((line.replace('\0', '') for line in csvfile), delimiter=','
       # quotechar='|'
       )
      NUM_ROWS = 50000
      i = 0
      for row in ireader:
        if i >= NUM_ROWS:
          break
        yield {
            "inputs": row[2],  # body
            "targets": row[1]  # issue title
        }
        i += 1
