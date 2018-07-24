"""Beam DoFns specific to `code_search.dataflow.transforms.github_batch_predict`."""

import apache_beam as beam

from code_search.t2t.query import get_encoder, encode_query


class EncodeExample(beam.DoFn):
  """Encode string to integer tokens.

  This is needed so that the data can be sent in
  for prediction. This DoFn adds a new "instances"
  key which contains the encoded input to be sent
  into a SavedModel instance later.

  Input element is a dict of the form:
    {
      "nwo": "STRING",
      "path": "STRING",
      "function_name": "STRING",
      "lineno": "STRING",
      "original_function": "STRING",
      "function_tokens": "STRING",
      "docstring_tokens": "STRING",
    }

  Output element is a dict of the form:
    {
      "nwo": "STRING",
      "path": "STRING",
      "function_name": "STRING",
      "lineno": "STRING",
      "original_function": "STRING",
      "function_tokens": "STRING",
      "docstring_tokens": "STRING",
      "instances": [
        {
          "input": {
            "b64": "STRING",
          }
        }
      ]
    }
  """
  def __init__(self, problem, data_dir):
    super(EncodeExample, self).__init__()

    self.problem = problem
    self.data_dir = data_dir

  @property
  def function_tokens_key(self):
    return u'function_tokens'

  @property
  def instances_key(self):
    return u'instances'

  def process(self, element, *args, **kwargs):
    encoder = get_encoder(self.problem, self.data_dir)
    encoded_function = encode_query(encoder, element.get(self.function_tokens_key))

    element[self.instances_key] = [{'input': {'b64': encoded_function}}]
    yield element


class ProcessPrediction(beam.DoFn):
  """Process results from PredictionDoFn.

  This class processes predictions from another
  DoFn. The main processing part involves converting
  the embedding into a serializable string for downstream
  processing. It also converts the "lineno" key into a unicode
  string.

  Input element is a dict of the form:
    {
      "nwo": "STRING",
      "path": "STRING",
      "function_name": "STRING",
      "lineno": "STRING",
      "original_function": "STRING",
      "function_tokens": "STRING",
      "docstring_tokens": "STRING",
      "instances": [
        {
          "input": {
            "b64": "STRING",
          }
        }
      ],
      "predictions": [
        {
          "outputs": [ # List of floats
            1.0,
            2.0,
            ...
          ]
        }
      ],
    }

  Output element is a dict of the form:
    {
      "nwo": "STRING",
      "path": "STRING",
      "function_name": "STRING",
      "lineno": "STRING",
      "original_function": "STRING",
      "function_embedding": "STRING",
    }
  """

  @property
  def function_embedding_key(self):
    return 'function_embedding'

  @property
  def predictions_key(self):
    return 'predictions'

  @property
  def pop_keys(self):
    return [
      'predictions',
      'docstring_tokens',
      'function_tokens',
      'instances',
    ]

  def process(self, element, *args, **kwargs):
    prediction = element.get(self.predictions_key)[0]['outputs']
    element[self.function_embedding_key] = ','.join([
      unicode(val) for val in prediction
    ])

    element['lineno'] = unicode(element['lineno'])

    for key in self.pop_keys:
      element.pop(key)

    yield element
