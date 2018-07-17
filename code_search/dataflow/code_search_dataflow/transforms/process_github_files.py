import io
import csv
import apache_beam as beam
from apache_beam.io.gcp.internal.clients import bigquery

from ..do_fns import ExtractFuncInfo
from ..do_fns import SplitRepoPath
from ..do_fns import TokenizeCodeDocstring


class ProcessGithubFiles(beam.PTransform):
  # pylint: disable=too-many-instance-attributes

  """A collection of `DoFn`s for Pipeline Transform. Reads the Github dataset from BigQuery
  and writes back the processed code-docstring pairs in a query-friendly format back to BigQuery
  table.
  """
  data_columns = ['nwo', 'path', 'function_name', 'lineno', 'original_function',
                       'function_tokens', 'docstring_tokens']
  data_types = ['STRING', 'STRING', 'STRING', 'INTEGER', 'STRING', 'STRING', 'STRING']

  def __init__(self, project, query_string, output_string, storage_bucket):
    super(ProcessGithubFiles, self).__init__()

    self.project = project
    self.query_string = query_string
    self.output_dataset, self.output_table = output_string.split(':')
    self.storage_bucket = storage_bucket

    self.num_shards = 10

  def expand(self, input_or_inputs):
    tokenize_result = (input_or_inputs
      | "Read Github Dataset" >> beam.io.Read(beam.io.BigQuerySource(query=self.query_string,
                                                          use_standard_sql=True))
      | "Split 'repo_path'" >> beam.ParDo(SplitRepoPath())
      | "Tokenize Code/Docstring Pairs" >> beam.ParDo(TokenizeCodeDocstring())
                                               .with_outputs('err_rows', main='rows')
    )

    #pylint: disable=expression-not-assigned
    (tokenize_result.err_rows
     | "Failed Row Tokenization" >> beam.io.WriteToBigQuery(project=self.project,
                                                        dataset=self.output_dataset,
                                                        table=self.output_table + '_failed',
                                                        schema=self.create_failed_output_schema())
    )
    # pylint: enable=expression-not-assigned


    info_result = (tokenize_result.rows
      | "Extract Function Info" >> beam.ParDo(ExtractFuncInfo(self.data_columns[2:]))
                                       .with_outputs('err_rows', main='rows')
    )

    #pylint: disable=expression-not-assigned
    (info_result.err_rows
     | "Failed Function Info" >> beam.io.WriteToBigQuery(project=self.project,
                                                        dataset=self.output_dataset,
                                                        table=self.output_table + '_failed',
                                                        schema=self.create_failed_output_schema())
    )
    # pylint: enable=expression-not-assigned

    processed_rows = (info_result.rows | "Flatten Rows" >> beam.FlatMap(lambda x: x))

    # pylint: disable=expression-not-assigned
    (processed_rows
     | "Filter Tiny Docstrings" >> beam.Filter(
        lambda row: len(row['docstring_tokens'].split(' ')) > 5)
     | "Format For Write" >> beam.Map(self.format_for_write)
     | "Write To File" >> beam.io.WriteToText('{}/data/pairs'.format(self.storage_bucket),
                                         file_name_suffix='.csv',
                                         num_shards=self.num_shards))
    # pylint: enable=expression-not-assigned

    return (processed_rows
      | "Save Tokens" >> beam.io.WriteToBigQuery(project=self.project,
                                                  dataset=self.output_dataset,
                                                  table=self.output_table,
                                                  schema=self.create_output_schema())
    )

  def format_for_write(self, row):
    """This method filters keys that we don't need in the
    final CSV. It must ensure that there are no multi-line
    column fields. For instance, 'original_function' is a
    multi-line string and makes CSV parsing hard for any
    derived Dataflow steps. This uses the CSV Writer
    to handle all edge cases like quote escaping."""

    filter_keys = [
        'original_function',
        'lineno',
    ]
    target_keys = [col for col in self.data_columns if col not in filter_keys]
    target_values = [row[key].encode('utf-8') for key in target_keys]

    with io.BytesIO() as fs:
      cw = csv.writer(fs)
      cw.writerow(target_values)
      result_str = fs.getvalue().strip('\r\n')

    return result_str

  def create_output_schema(self):
    table_schema = bigquery.TableSchema()

    for column, data_type in zip(self.data_columns, self.data_types):
      field_schema = bigquery.TableFieldSchema()
      field_schema.name = column
      field_schema.type = data_type
      field_schema.mode = 'nullable'
      table_schema.fields.append(field_schema)

    return table_schema

  def create_failed_output_schema(self):
    table_schema = bigquery.TableSchema()

    for column, data_type in zip(self.data_columns[:2] + ['content'],
                                 self.data_types[:2] + ['STRING']):
      field_schema = bigquery.TableFieldSchema()
      field_schema.name = column
      field_schema.type = data_type
      field_schema.mode = 'nullable'
      table_schema.fields.append(field_schema)

    return table_schema
