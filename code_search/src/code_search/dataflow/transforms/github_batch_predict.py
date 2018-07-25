import apache_beam as beam
import kubeflow_batch_predict.dataflow.batch_prediction as batch_prediction

import code_search.dataflow.do_fns.github_batch_predict as github_batch_predict
import code_search.dataflow.transforms.github_bigquery as github_bigquery


class GithubBatchPredict(beam.PTransform):
  """Batch Prediction for Github dataset.

  This Beam pipeline takes in the transformed dataset,
  prepares each element's function tokens for prediction
  by encoding it into base64 format and returns an updated
  dictionary element with the embedding for further processing.

  This transform creates following tables in the `target_dataset`
  which are defined as properties for easy modification.
    - `self.index_table`
  """

  def __init__(self, project, target_dataset, problem, data_dir, saved_model_dir):
    super(GithubBatchPredict, self).__init__()

    self.project = project
    self.target_dataset = target_dataset
    self.problem = problem
    self.data_dir = data_dir
    self.saved_model_dir = saved_model_dir

  @property
  def index_table(self):
    return 'search_index'

  def expand(self, input_or_inputs):
    batch_predict = (input_or_inputs
      | "Prepare Encoded Input" >> beam.ParDo(github_batch_predict.EncodeFunctionTokens(self.problem,
                                                                                        self.data_dir))
      | "Execute Predictions" >> beam.ParDo(batch_prediction.PredictionDoFn(),
                                            self.saved_model_dir).with_outputs('err',
                                                                               main='main')
    )

    predictions = batch_predict.main

    formatted_predictions = (predictions
      | "Process Predictions" >> beam.ParDo(github_batch_predict.ProcessFunctionEmbedding())
    )

    (formatted_predictions  # pylint: disable=expression-not-assigned
      | "Save Index Data" >> github_bigquery.WriteGithubIndexData(self.project,
                                                                  self.target_dataset,
                                                                  self.index_table)
    )

    return formatted_predictions
