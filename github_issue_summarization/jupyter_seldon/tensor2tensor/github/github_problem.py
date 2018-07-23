import pandas as pd
from tensor2tensor.utils import registry
from tensor2tensor.models import transformer
from tensor2tensor.data_generators import problem
from tensor2tensor.data_generators import text_problems


@registry.register_problem
class GithubIssueSummarizationProblem(text_problems.Text2TextProblem):
  """Predict issue summary from issue body. Using Github issue data."""

  @property
  def approx_vocab_size(self):
    return 2**12  # ~4k

  @property
  def is_generate_per_split(self):
    # generate_data will NOT shard the data into TRAIN and EVAL for us.
    return False

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

  def generate_samples(self, data_dir, tmp_dir, dataset_split):  # pylint: disable=unused-argument, no-self-use
    chunksize = 200000
    for issue_data in pd.read_csv(
        'csv_data/github_issues_10000.csv', chunksize=chunksize):
      issue_body_data = issue_data.body.tolist()
      issue_title_data = issue_data.issue_title.tolist()
      n = len(issue_title_data)
      for i in range(n):
        yield {"inputs": issue_body_data[i], "targets": issue_title_data[i]}


# Smaller than the typical translate model, and with more regularization
@registry.register_hparams
def transformer_github_issues():
  hparams = transformer.transformer_base()
  hparams.num_hidden_layers = 2
  hparams.hidden_size = 128
  hparams.filter_size = 512
  hparams.num_heads = 4
  hparams.attention_dropout = 0.6
  hparams.layer_prepostprocess_dropout = 0.6
  hparams.learning_rate = 0.05
  return hparams


# hyperparameter tuning ranges
@registry.register_ranged_hparams
def transformer_github_issues_range(rhp):
  rhp.set_float("learning_rate", 0.05, 0.25, scale=rhp.LOG_SCALE)
  rhp.set_int("num_hidden_layers", 2, 4)
  rhp.set_discrete("hidden_size", [128, 256, 512])
  rhp.set_float("attention_dropout", 0.4, 0.7)
