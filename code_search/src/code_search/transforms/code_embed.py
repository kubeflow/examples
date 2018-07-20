import apache_beam as beam
from kubeflow_batch_predict.dataflow.batch_prediction import PredictionDoFn

from ..do_fns.embeddings import EncodeExample
from ..do_fns.embeddings import ProcessPrediction

from .github_bigquery import ReadProcessedGithubData
from .github_bigquery import WriteGithubIndexData

class GithubBatchPredict(beam.PTransform):
  """Batch Prediction for Github dataset"""

  def __init__(self, project, problem, data_dir, saved_model_dir):
    super(GithubBatchPredict, self).__init__()

    self.project = project
    self.problem = problem
    self.data_dir = data_dir
    self.saved_model_dir = saved_model_dir

    ##
    # Target dataset and table to store prediction outputs.
    # Non-configurable for now.
    #
    self.index_dataset = 'code_search'
    self.index_table = 'search_index'

    self.batch_size = 100

  def expand(self, input_or_inputs):
    rows = (input_or_inputs
      | "Read Processed Github Dataset" >> ReadProcessedGithubData(self.project)
    )

    batch_predict = (rows
      | "Prepare Encoded Input" >> beam.ParDo(EncodeExample(self.problem, self.data_dir))
      | "Execute Predictions" >> beam.ParDo(PredictionDoFn(),
                                            self.saved_model_dir).with_outputs("errors",
                                                                               main="main")
    )

    predictions, errors = batch_predict.main, batch_predict.errors

    formatted_predictions = (predictions
      | "Process Predictions" >> beam.ParDo(ProcessPrediction())
    )

    (formatted_predictions
      | "Save Index Data" >> WriteGithubIndexData(self.project,
                                                  self.index_dataset, self.index_table,
                                                  batch_size=self.batch_size)
    )

    return formatted_predictions
