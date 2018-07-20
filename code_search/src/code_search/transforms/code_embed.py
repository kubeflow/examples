import apache_beam as beam
from apache_beam.io.gcp.internal.clients import bigquery
from kubeflow_batch_predict.dataflow.batch_prediction import PredictionDoFn

from ..do_fns.embeddings import GithubCSVToDict, GithubDictToCSV
from ..do_fns.embeddings import EncodeExample, ProcessPrediction

class GithubCodeEmbed(beam.PTransform):
  """Embed text in CSV files using the trained model."""

  def __init__(self, project, input_table, saved_model_dir, problem, data_dir, storage_bucket):
    super(GithubCodeEmbed, self).__init__()

    self.project = project
    self.input_table = input_table
    self.query_string = """
      SELECT `nwo`, `path`, `function_name`, `lineno`, `original_function`, `function_tokens` FROM `{}.{}` LIMIT 100
    """.format(self.project, self.input_table)
    self.saved_model_dir = saved_model_dir
    self.problem = problem
    self.data_dir = data_dir

    self.storage_bucket = storage_bucket
    self.num_shards = 10

  def expand(self, input_or_inputs):
    rows = (input_or_inputs
      | "Read Pre-processed Dataset" >> beam.io.Read(beam.io.BigQuerySource(query=self.query_string,
                                                                     project=self.project,
                                                                     use_standard_sql=True))
    )

    batch_predict = (rows
      | "Prepare Encoded Input" >> beam.ParDo(EncodeExample(self.problem, self.data_dir))
      | "Execute predictions" >> beam.ParDo(PredictionDoFn(),
                                            self.saved_model_dir).with_outputs("errors",
                                                                               main="main")
    )

    predictions, errors = batch_predict.main, batch_predict.errors

    (predictions
      | "Process Predictions" >> beam.ParDo(ProcessPrediction())
      | "Save Tokens" >> beam.io.WriteToBigQuery(project=self.project,
                                                 dataset='code_search',
                                                 table='search_index',
                                                 schema=self.create_output_schema(),
                                                 batch_size=10)
    )

    return rows

  @staticmethod
  def create_output_schema():
    data_columns = ['nwo', 'path', 'function_name', 'lineno', 'original_function', 'function_embedding']
    data_types = ['STRING', 'STRING', 'STRING', 'INTEGER', 'STRING', 'STRING']
    table_schema = bigquery.TableSchema()

    for column, data_type in zip(data_columns, data_types):
      field_schema = bigquery.TableFieldSchema()
      field_schema.name = column
      field_schema.type = data_type
      field_schema.mode = 'nullable'
      table_schema.fields.append(field_schema)

    return table_schema
