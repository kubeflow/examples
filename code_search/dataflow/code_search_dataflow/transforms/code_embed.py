import apache_beam as beam
from kubeflow_batch_predict.dataflow.batch_prediction import PredictionDoFn


class GithubCodeEmbed(beam.PTransform):
  """Embed text in CSV files using the trained model.

  TODO(sanyamkapoor): Fill in details using PredictionDoFn
  """

  def __init__(self):
    super(GithubCodeEmbed, self).__init__()

  def expand(self, input_or_inputs):
    pass
