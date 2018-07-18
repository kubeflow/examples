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
    encoder = get_encoder(self.problem, self.data_dir)
    encoded_function = encode_query(encoder, element['function_tokens'])
    encoded_docstring = encode_query(encoder, element['docstring_tokens'])

    element['instances'] = [
        {'input': {'b64': encoded_function}},
        {'input': {'b64': encoded_docstring}},
    ]
    yield element


class ProcessPrediction(beam.DoFn):
  """Process results from PredictionDoFn.

  This class processes predictions from another
  DoFn, to make sure it is a correctly formatted dict.
  """
  def process(self, element, *args, **kwargs):
    element['function_embedding'] = element['predictions'][0]['outputs']
    element['docstring_embedding'] = element['predictions'][1]['outputs']

    element.pop('instances')
    element.pop('predictions')

    yield element
