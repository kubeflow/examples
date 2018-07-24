import apache_beam as beam
import kubeflow_batch_predict.dataflow.batch_prediction as batch_prediction

import code_search.dataflow.do_fns.embeddings as embeddings
import code_search.dataflow.transforms.github_bigquery as github_bigquery


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
      | "Read Processed Github Dataset" >> github_bigquery.ReadProcessedGithubData(self.project)
    )

    batch_predict = (rows
      | "Prepare Encoded Input" >> beam.ParDo(embeddings.EncodeExample(self.problem,
                                                                       self.data_dir))
      | "Execute Predictions" >> beam.ParDo(batch_prediction.PredictionDoFn(),
                                            self.saved_model_dir).with_outputs("errors",
                                                                               main="main")
    )

    predictions = batch_predict.main

    formatted_predictions = (predictions
      | "Process Predictions" >> beam.ParDo(embeddings.ProcessPrediction())
    )

    (formatted_predictions  # pylint: disable=expression-not-assigned
      | "Save Index Data" >> github_bigquery.WriteGithubIndexData(self.project,
                                                                  self.index_dataset,
                                                                  self.index_table,
                                                                  batch_size=self.batch_size)
    )

    return formatted_predictions
