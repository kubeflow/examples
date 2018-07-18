"""Beam DoFns for prediction related tasks"""

import csv
import apache_beam as beam
from cStringIO import StringIO
from ..transforms.process_github_files import ProcessGithubFiles
from ..t2t.query import get_encoder, encode_query

class GithubCSVToDict(beam.DoFn):
  """Split a text row and convert into a dict."""

  def process(self, element, *args, **kwargs):  # pylint: disable=unused-argument,no-self-use
    element = element.encode('utf-8')
    row = StringIO(element)
    reader = csv.reader(row, delimiter=',')

    keys = ProcessGithubFiles.get_key_list()
    values = next(reader)

    result = dict(zip(keys, values))
    yield result


class EncodeExample(beam.DoFn):
  """Encode string to integer tokens.

  This is needed so that the data can be sent in
  for prediction
  """
  def __init__(self, problem, data_dir):
    super(EncodeExample, self).__init__()

    self.problem = problem
    self.data_dir = data_dir

  def process(self, element, *args, **kwargs):  # pylint: disable=unused-argument
    function_token_string = element['function_tokens']

    encoder = get_encoder(self.problem, self.data_dir)
    encoded_example = encode_query(encoder, function_token_string)

    element['input'] = {'b64': encoded_example}
    yield element


class ProcessPrediction(beam.DoFn):
  """Process results from PredictionDoFn

  TODO(sanyamkapoor):
  This class processes predictions from another
  DoFn, to make sure it is a correctly formatted dict.
  """
  def process(self, element, *args, **kwargs):
    data = element
    yield element
