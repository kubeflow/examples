"""Beam DoFns for Github related tasks"""
import time
import logging
import apache_beam as beam
from apache_beam import pvalue
from apache_beam.metrics import Metrics


class SplitRepoPath(beam.DoFn):
  # pylint: disable=abstract-method
  """Split the space-delimited file `repo_path` into owner repository (`nwo`)
  and file path (`path`)"""

  def process(self, element, *args, **kwargs): # pylint: disable=unused-argument,no-self-use
    nwo, path = element.pop('repo_path').split(' ', 1)
    element['nwo'] = nwo
    element['path'] = path
    yield element


class TokenizeCodeDocstring(beam.DoFn):
  # pylint: disable=abstract-method
  """Compute code/docstring pairs from incoming BigQuery row dict"""
  def __init__(self):
    super(TokenizeCodeDocstring, self).__init__()

    self.tokenization_time_ms = Metrics.counter(self.__class__, 'tokenization_time_ms')

  def process(self, element, *args, **kwargs): # pylint: disable=unused-argument,no-self-use
    try:
      from ..utils import get_function_docstring_pairs

      start_time = time.time()
      element['pairs'] = get_function_docstring_pairs(element.pop('content'))
      self.tokenization_time_ms.inc(int((time.time() - start_time) * 1000.0))

      yield element
    except Exception as e: #pylint: disable=broad-except
      logging.warning('Tokenization failed, %s', e.message)
      yield pvalue.TaggedOutput('err_rows', element)


class ExtractFuncInfo(beam.DoFn):
  # pylint: disable=abstract-method
  """Convert pair tuples from `TokenizeCodeDocstring` into dict containing query-friendly keys"""
  def __init__(self, info_keys):
    super(ExtractFuncInfo, self).__init__()

    self.info_keys = info_keys

  def process(self, element, *args, **kwargs): # pylint: disable=unused-argument
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
