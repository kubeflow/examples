"""Beam DoFns specific to `code_search.dataflow.transforms.github_dataset`."""

import time
import logging
import apache_beam as beam
from apache_beam import pvalue
from apache_beam.metrics import Metrics


class SplitRepoPath(beam.DoFn):
  """Update element keys to separate repo path and file path.

  This DoFn's only purpose is to be used after
  `code_search.dataflow.transforms.github_bigquery.ReadGithubDataset`
  to split the `repo_path` dictionary key into two new keys
  `nwo` (repository path) and `path` (the relative file path).
  The original dataset has these two values separate by a space
  character.
  """

  def process(self, element, *args, **kwargs):
    nwo, path = element.pop('repo_path').split(' ', 1)
    element['nwo'] = nwo
    element['path'] = path
    yield element


class TokenizeFunctionDocstrings(beam.DoFn):
  """Tokenize function and docstrings.

  This DoFn takes in the rows from BigQuery and tokenizes
  the file content present in the 'content' key. This
  yields an updated dictionary with the new tokenized
  data in the 'pairs' key. In cases where the tokenization
  fails, a side output is returned.
  """

  def process(self, element, *args, **kwargs):
    try:
      import code_search.dataflow.utils as utils

      element['pairs'] = utils.get_function_docstring_pairs(element.get('content'))

      yield element
    except Exception as e: #pylint: disable=broad-except
      logging.warning('Tokenization failed, %s', e.message)
      yield pvalue.TaggedOutput('err', element)


class ExtractFuncInfo(beam.DoFn):
  # pylint: disable=abstract-method
  """Convert pair tuples to dict.

  This takes a list of values from `TokenizeCodeDocstring`
  and converts into a dictionary so that values can be
  indexed by names instead of indices. `info_keys` is the
  list of names of those values in order which will become
  the keys of each new dict.
  """
  def __init__(self, info_keys):
    super(ExtractFuncInfo, self).__init__()

    self.info_keys = info_keys

  def process(self, element):
    try:
      info_rows = [dict(zip(self.info_keys, pair)) for pair in element.pop('pairs')]
      info_rows = [self.merge_two_dicts(info_dict, element) for info_dict in info_rows]
      info_rows = map(self.dict_to_unicode, info_rows)
      yield info_rows
    except Exception as e: #pylint: disable=broad-except
      logging.warning('Function Info extraction failed, %s', e.message)
      yield pvalue.TaggedOutput('err_rows', element)

  @staticmethod
  def merge_two_dicts(dict_a, dict_b):
    result = dict_a.copy()
    result.update(dict_b)
    return result

  @staticmethod
  def dict_to_unicode(data_dict):
    for k, v in data_dict.items():
      if isinstance(v, str):
        data_dict[k] = v.decode('utf-8', 'ignore')
    return data_dict
