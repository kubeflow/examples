"""Beam DoFns for prediction related tasks"""
import io
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


class GithubDictToCSV(beam.DoFn):
  """Convert dictionary to writable CSV string."""

  def process(self, element, *args, **kwargs):
    element['function_embedding'] = ','.join(str(val) for val in element['function_embedding'])

    target_keys = ['nwo', 'path', 'function_name', 'function_embedding']
    target_values = [element[key].encode('utf-8') for key in target_keys]

    with io.BytesIO() as fs:
      cw = csv.writer(fs)
      cw.writerow(target_values)
      result_str = fs.getvalue().strip('\r\n')

    return result_str


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

    element['instances'] = [{'input': {'b64': encoded_function}}]
    yield element


class ProcessPrediction(beam.DoFn):
  """Process results from PredictionDoFn.

  This class processes predictions from another
  DoFn, to make sure it is a correctly formatted dict.
  """
  def process(self, element, *args, **kwargs):
    element['function_embedding'] = element['predictions'][0]['outputs']

    element.pop('instances')
    element.pop('predictions')

    yield element
