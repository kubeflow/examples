import apache_beam as beam
from kubeflow_batch_predict.dataflow.batch_prediction import PredictionDoFn

from ..do_fns.embeddings import GithubCSVToDict
from ..do_fns.embeddings import EncodeExample

class GithubCodeEmbed(beam.PTransform):
  """Embed text in CSV files using the trained model.

  TODO(sanyamkapoor): Fill in details using PredictionDoFn
  """

  def __init__(self, input_files, saved_model_dir, problem, data_dir):
    super(GithubCodeEmbed, self).__init__()

    self.input_files = input_files
    self.saved_model_dir = saved_model_dir
    self.problem = problem
    self.data_dir = data_dir

  def expand(self, input_or_inputs):
    csv_dict_rows = (input_or_inputs
      | "Read from CSV Files" >> beam.io.ReadFromText(self.input_files)
      | "Split Row Text" >> beam.ParDo(GithubCSVToDict())
    )

    batch_predict = (csv_dict_rows
      | "Prepare Encoded Input" >> beam.ParDo(EncodeExample(self.problem, self.data_dir))
      # | "Make predictions" >> beam.ParDo(PredictionDoFn(framework='TENSORFLOW'),
      #                                    self.saved_model_dir).with_outputs("errors", main="main")
    )

    # predictions, errors = batch_predict.main, batch_predict.errors

    return csv_dict_rows
