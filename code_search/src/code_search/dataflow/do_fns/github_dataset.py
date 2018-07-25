"""Beam DoFns specific to `code_search.dataflow.transforms.github_dataset`."""

import logging
import apache_beam as beam
from apache_beam import pvalue


class SplitRepoPath(beam.DoFn):
  """Update element keys to separate repo path and file path.

  This DoFn's only purpose is to be used after
  `code_search.dataflow.transforms.github_bigquery.ReadGithubDataset`
  to split the source dictionary key into two target keys which
  represent the repository owner and relative file path.
  The original dataset has these two values separate by a space
  character. All values are unicode for serialization.

  Input element is a dict of the form:
    {
      "repo_path": "STRING",
      "content": "STRING",
    }
  Output element is a dict of the form:
    {
      "nwo": "STRING",
      "path": "STRING",
      "content": "STRING",
    }
  """

  @property
  def source_key(self):
    return u'repo_path'

  @property
  def target_keys(self):
    return [u'nwo', u'path']

  def process(self, element, *_args, **_kwargs):
    values = element.pop(self.source_key).split(' ', 1)

    for key, value in zip(self.target_keys, values):
      element[key] = value

    yield element


class TokenizeFunctionDocstrings(beam.DoFn):
  """Tokenize function and docstrings.

  This DoFn takes in the rows from BigQuery and tokenizes
  the file content present in the content key. This
  yields an updated dictionary with the new tokenized
  data in the pairs key. In cases where the tokenization
  fails, a side output is returned. All values are unicode for
  serialization.

  Input element is a dict of the form:
    {
      "nwo": "STRING",
      "path": "STRING",
      "content": "STRING",
    }
  Output element is a list of the form:
    [
      {
        "nwo": "STRING",
        "path": "STRING",
        "function_name": "STRING",
        "lineno": "STRING",
        "original_function": "STRING",
        "function_tokens": "STRING",
        "docstring_tokens": "STRING",
      },
      ...
    ]
  """

  @property
  def content_key(self):
    return 'content'

  @property
  def info_keys(self):
    return [
      u'function_name',
      u'lineno',
      u'original_function',
      u'function_tokens',
      u'docstring_tokens',
    ]

  def process(self, element, *_args, **_kwargs):
    try:
      import code_search.dataflow.utils as utils

      content_blob = element.pop(self.content_key)
      pairs = utils.get_function_docstring_pairs(content_blob)

      result = [
        dict(zip(self.info_keys, pair_tuple), **element)
        for pair_tuple in pairs
      ]

      yield result
    except Exception as e:  # pylint: disable=broad-except
      logging.warning('Tokenization failed, %s', e.message)
      yield pvalue.TaggedOutput('err', element)
