import apache_beam as beam

import code_search.dataflow.do_fns.github_dataset as gh_do_fns
import code_search.dataflow.transforms.github_bigquery as gh_bq


class TransformGithubDataset(beam.PTransform):
  """Transform the BigQuery Github Dataset.

  This is a Beam Pipeline which reads the Github Dataset from
  BigQuery, tokenizes functions and docstrings in Python files,
  and dumps into a new BigQuery dataset for further processing.
  All tiny docstrings (smaller than `self.min_docstring_tokens`)
  are filtered out.

  This transform creates following tables in the `target_dataset`
  which are defined as properties for easy modification.
    - `self.failed_tokenize_table`
    - `self.pairs_table`
  """

  def __init__(self, project, target_dataset,
               pairs_table=gh_bq.PAIRS_TABLE,
               failed_tokenize_table=gh_bq.FAILED_TOKENIZE_TABLE):
    super(TransformGithubDataset, self).__init__()

    self.project = project
    self.target_dataset = target_dataset
    self.pairs_table = pairs_table
    self.failed_tokenize_table = failed_tokenize_table

  @property
  def min_docstring_tokens(self):
    return 5

  def expand(self, input_or_inputs):
    tokenize_result = (input_or_inputs
     | "Split 'repo_path'" >> beam.ParDo(gh_do_fns.SplitRepoPath())
     | "Tokenize Code/Docstring Pairs" >> beam.ParDo(
        gh_do_fns.TokenizeFunctionDocstrings()).with_outputs('err', main='rows')
    )

    pairs, tokenize_errors = tokenize_result.rows, tokenize_result.err

    (tokenize_errors  # pylint: disable=expression-not-assigned
     | "Failed Tokenization" >> gh_bq.WriteFailedTokenizedData(self.project, self.target_dataset,
                                                               self.failed_tokenize_table)
    )

    flat_rows = (pairs
      | "Flatten Rows" >> beam.FlatMap(lambda x: x)
      | "Filter Tiny Docstrings" >> beam.Filter(
        lambda row: len(row['docstring_tokens'].split(' ')) > self.min_docstring_tokens)
    )

    (flat_rows  # pylint: disable=expression-not-assigned
      | "Save Tokens" >> gh_bq.WriteTokenizedData(self.project, self.target_dataset,
                                                  self.pairs_table)
    )

    return flat_rows
