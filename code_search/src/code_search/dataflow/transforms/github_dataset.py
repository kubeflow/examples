import io
import csv
import apache_beam as beam
import apache_beam.io.gcp.internal.clients as clients

import code_search.dataflow.do_fns.github_dataset as gh_do_fns
import code_search.dataflow.transforms.github_bigquery as gh_bq


class TransformGithubDataset(beam.PTransform):
  """Transform the BigQuery Github Dataset.

  This is a Beam Pipeline which reads the Github Dataset from
  BigQuery, tokenizes functions and docstrings in Python files,
  and dumps into a new BigQuery dataset for further processing.
  """

  data_columns = ['nwo', 'path', 'function_name', 'lineno', 'original_function',
                       'function_tokens', 'docstring_tokens']
  data_types = ['STRING', 'STRING', 'STRING', 'INTEGER', 'STRING', 'STRING', 'STRING']

  def __init__(self, project):
    super(TransformGithubDataset, self).__init__()

    self.project = project

  def expand(self, input_or_inputs):
    tokenize_result = (input_or_inputs
     | "Read Github Dataset" >> gh_bq.ReadGithubDataset(self.project)
     | "Split 'repo_path'" >> beam.ParDo(gh_do_fns.SplitRepoPath())
     | "Tokenize Code/Docstring Pairs" >> beam.ParDo(gh_do_fns.TokenizeFunctionDocstrings()).with_outputs('err', main='rows')
    )

    (tokenize_result.err  # pylint: disable=expression-not-assigned
     | "Failed Row Tokenization" >> beam.io.WriteToBigQuery(project=self.project,
                                                        dataset=self.output_dataset,
                                                        table=self.output_table + '_failed',
                                                        schema=self.create_failed_output_schema())
    )

    info_result = (tokenize_result.rows
      | "Extract Function Info" >> beam.ParDo(gh_do_fns.ExtractFuncInfo(self.data_columns[2:]))
                                       .with_outputs('err_rows', main='rows')
    )

    (info_result.err_rows  # pylint: disable=expression-not-assigned
     | "Failed Function Info" >> beam.io.WriteToBigQuery(project=self.project,
                                                        dataset=self.output_dataset,
                                                        table=self.output_table + '_failed',
                                                        schema=self.create_failed_output_schema())
    )

    processed_rows = (info_result.rows | "Flatten Rows" >> beam.FlatMap(lambda x: x))

    (processed_rows  # pylint: disable=expression-not-assigned
     | "Filter Tiny Docstrings" >> beam.Filter(
        lambda row: len(row['docstring_tokens'].split(' ')) > 5)
     | "Format For Write" >> beam.Map(self.format_for_write)
     | "Write To File" >> beam.io.WriteToText('{}/data/pairs'.format(self.storage_bucket),
                                         file_name_suffix='.csv',
                                         num_shards=self.num_shards))

    return (processed_rows
      | "Save Tokens" >> beam.io.WriteToBigQuery(project=self.project,
                                                  dataset=self.output_dataset,
                                                  table=self.output_table,
                                                  schema=self.create_output_schema())
    )

  @staticmethod
  def get_key_list():
    filter_keys = [
        'original_function',
        'lineno',
    ]
    key_list = [col for col in TransformGithubDataset.data_columns
                if col not in filter_keys]
    return key_list

  def format_for_write(self, row):
    """This method filters keys that we don't need in the
    final CSV. It must ensure that there are no multi-line
    column fields. For instance, 'original_function' is a
    multi-line string and makes CSV parsing hard for any
    derived Dataflow steps. This uses the CSV Writer
    to handle all edge cases like quote escaping."""

    target_keys = self.get_key_list()
    target_values = [row[key].encode('utf-8') for key in target_keys]

    with io.BytesIO() as fs:
      cw = csv.writer(fs)
      cw.writerow(target_values)
      result_str = fs.getvalue().strip('\r\n')

    return result_str

  def create_output_schema(self):
    table_schema = clients.bigquery.TableSchema()

    for column, data_type in zip(self.data_columns, self.data_types):
      field_schema = clients.bigquery.TableFieldSchema()
      field_schema.name = column
      field_schema.type = data_type
      field_schema.mode = 'nullable'
      table_schema.fields.append(field_schema)

    return table_schema

  def create_failed_output_schema(self):
    table_schema = clients.bigquery.TableSchema()

    for column, data_type in zip(self.data_columns[:2] + ['content'],
                                 self.data_types[:2] + ['STRING']):
      field_schema = clients.bigquery.TableFieldSchema()
      field_schema.name = column
      field_schema.type = data_type
      field_schema.mode = 'nullable'
      table_schema.fields.append(field_schema)

    return table_schema
