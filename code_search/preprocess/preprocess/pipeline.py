import os
import logging
import time
`import csv
import io
import apache_beam as beam
from apache_beam import pvalue
from apache_beam.metrics import Metrics
from apache_beam.options.pipeline_options import StandardOptions, PipelineOptions, \
  GoogleCloudOptions, SetupOptions, WorkerOptions
from apache_beam.io.gcp.internal.clients import bigquery


def create_pipeline_opts(args):
  """Create standard Pipeline Options for Google Cloud Dataflow"""
  options = PipelineOptions()
  options.view_as(StandardOptions).runner = 'DataflowRunner'

  google_cloud_options = options.view_as(GoogleCloudOptions)
  google_cloud_options.project = args.project
  google_cloud_options.job_name = args.job_name
  google_cloud_options.temp_location = '{}/temp'.format(args.storage_bucket)
  google_cloud_options.staging_location = '{}/staging'.format(args.storage_bucket)

  options.view_as(WorkerOptions).num_workers = args.num_workers
  options.view_as(WorkerOptions).max_num_workers = args.max_num_workers
  options.view_as(WorkerOptions).machine_type = args.machine_type

  # Point to `setup.py` to allow Dataflow runner to install the package
  options.view_as(SetupOptions).setup_file = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'setup.py')

  return options


class SplitRepoPath(beam.DoFn):
  # pylint: disable=abstract-method
  """Split the space-delimited file `repo_path` into owner repository (`nwo`)
  and file path (`path`)"""

  def process(self, element, *args, **kwargs): # pylint: disable=unused-argument,no-self-use
    nwo, path = element.pop('repo_path').split(' ', 1)
    element['nwo'] = nwo
    element['path'] = path
    yield element


class TokenizeCodeDocstring(beam.DoFn):
  # pylint: disable=abstract-method
  """Compute code/docstring pairs from incoming BigQuery row dict"""
  def __init__(self):
    super(TokenizeCodeDocstring, self).__init__()

    self.tokenization_time_ms = Metrics.counter(self.__class__, 'tokenization_time_ms')

  def process(self, element, *args, **kwargs): # pylint: disable=unused-argument,no-self-use
    try:
      from preprocess.tokenizer import get_function_docstring_pairs

      start_time = time.time()
      element['pairs'] = get_function_docstring_pairs(element.pop('content'))
      self.tokenization_time_ms.inc(int((time.time() - start_time) * 1000.0))

      yield element
    except Exception as e: #pylint: disable=broad-except
      logging.warning('Tokenization failed, %s', e.message)
      yield pvalue.TaggedOutput('err_rows', element)


class ExtractFuncInfo(beam.DoFn):
  # pylint: disable=abstract-method
  """Convert pair tuples from `TokenizeCodeDocstring` into dict containing query-friendly keys"""
  def __init__(self, info_keys):
    super(ExtractFuncInfo, self).__init__()

    self.info_keys = info_keys

  def process(self, element, *args, **kwargs): # pylint: disable=unused-argument
    try:
      info_rows = [dict(zip(self.info_keys, pair)) for pair in element.pop('pairs')]
      info_rows = [self.merge_two_dicts(info_dict, element) for info_dict in info_rows]
      info_rows = map(self.dict_to_unicode, info_rows)
      yield info_rows
    except Exception as e: #pylint: disable=broad-except
      logging.warning('Function Info extraction failed, %s', e.message)
      yield pvalue.TaggedOutput('err_rows', element)

  @staticmethod
  def merge_two_dicts(dict_a, dict_b):
    result = dict_a.copy()
    result.update(dict_b)
    return result

  @staticmethod
  def dict_to_unicode(data_dict):
    for k, v in data_dict.items():
      if isinstance(v, str):
        data_dict[k] = v.decode('utf-8', 'ignore')
    return data_dict


class ProcessGithubFiles(beam.PTransform):
  # pylint: disable=too-many-instance-attributes

  """A collection of `DoFn`s for Pipeline Transform. Reads the Github dataset from BigQuery
  and writes back the processed code-docstring pairs in a query-friendly format back to BigQuery
  table.
  """
  def __init__(self, project, query_string, output_string, storage_bucket):
    super(ProcessGithubFiles, self).__init__()

    self.project = project
    self.query_string = query_string
    self.output_dataset, self.output_table = output_string.split(':')
    self.storage_bucket = storage_bucket

    self.data_columns = ['nwo', 'path', 'function_name', 'lineno', 'original_function',
                         'function_tokens', 'docstring_tokens']
    self.data_types = ['STRING', 'STRING', 'STRING', 'INTEGER', 'STRING', 'STRING', 'STRING']

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
