import os
import apache_beam as beam
import apache_beam.io as io
from apache_beam.options.pipeline_options import StandardOptions, PipelineOptions, GoogleCloudOptions, SetupOptions
from apache_beam.io.gcp.internal.clients import bigquery


def create_pipeline_opts(args):
    """Create standard Pipeline Options for Google Cloud Dataflow"""
    options = PipelineOptions()
    options.view_as(StandardOptions).runner = 'DataflowRunner'

    google_cloud_options = options.view_as(GoogleCloudOptions)
    google_cloud_options.project = args.project
    google_cloud_options.job_name = args.job_name
    google_cloud_options.temp_location = '{}/{}/temp'.format(args.storage_bucket, args.job_name)
    google_cloud_options.staging_location = '{}/{}/staging'.format(args.storage_bucket, args.job_name)

    # Point to `setup.py` to allow Dataflow runner to install the package
    options.view_as(SetupOptions).setup_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'setup.py')

    return options


class SplitRepoPath(beam.DoFn):
    """Split the space-delimited file `repo_path` into owner repository (`nwo`) and file path (`path`) """
    def process(self, element, *args, **kwargs):
        nwo, path = element.pop('repo_path').split(' ', 1)
        element['nwo'] = nwo
        element['path'] = path
        yield element


class TokenizeCodeDocstring(beam.DoFn):
    """Compute code/docstring pairs from incoming BigQuery row dict"""
    def process(self, element, *args, **kwargs):
        from preprocess.tokenizer import get_function_docstring_pairs
        element['pairs'] = get_function_docstring_pairs(element.pop('content'))
        yield element


class ExtractFuncInfo(beam.DoFn):
    """Convert pair tuples from `TokenizeCodeDocstring` into dict containing query-friendly keys"""
    def __init__(self, info_keys):
        super(ExtractFuncInfo, self).__init__()

        self.info_keys = info_keys

    def process(self, element, *args, **kwargs):
        info_rows = map(lambda pair: dict(zip(self.info_keys, pair)), element.pop('pairs'))
        info_rows = map(lambda info_dict: self.merge_two_dicts(info_dict, element), info_rows)
        info_rows = map(self.dict_to_unicode, info_rows)
        yield info_rows

    @staticmethod
    def merge_two_dicts(dict_a, dict_b):
        result = dict_a.copy()
        result.update(dict_b)
        return result

    @staticmethod
    def dict_to_unicode(data_dict):
        for k, v in data_dict.items():
            if isinstance(v, str):
                data_dict[k] = v.encode('utf-8', 'ignore')
        return data_dict


class BigQueryGithubFiles(beam.PTransform):
    """A collection of `DoFn`s for Pipeline Transform. Reads the Github dataset from BigQuery
    and writes back the processed code-docstring pairs in a query-friendly format back to BigQuery
    table.
    """
    def __init__(self, project, query_string, output_string):
        super(BigQueryGithubFiles, self).__init__()

        self.project = project
        self.query_string = query_string
        self.output_dataset, self.output_table = output_string.split(':')

        self.data_columns = ['nwo', 'path', 'function_name', 'lineno', 'original_function',
                             'function_tokens', 'docstring_tokens']
        self.data_types = ['STRING', 'STRING', 'STRING', 'INTEGER', 'STRING', 'STRING', 'STRING']

    def expand(self, pcoll):
        return (pcoll
                | "Read BigQuery Rows" >> io.Read(io.BigQuerySource(query=self.query_string, use_standard_sql=True))
                | "Split 'repo_path'" >> beam.ParDo(SplitRepoPath())
                | "Tokenize Code/Docstring Pairs" >> beam.ParDo(TokenizeCodeDocstring())
                | "Extract Function Info" >> beam.ParDo(ExtractFuncInfo(self.data_columns[2:]))
                | "Flatten Rows" >> beam.FlatMap(lambda x: x)
                | "Write to BigQuery" >> io.WriteToBigQuery(project=self.project,
                                                            dataset=self.output_dataset,
                                                            table=self.output_table,
                                                            schema=self.create_output_schema())
                )

    def create_output_schema(self):
        table_schema = bigquery.TableSchema()

        for column, data_type in zip(self.data_columns, self.data_types):
            field_schema = bigquery.TableFieldSchema()
            field_schema.name = column
            field_schema.type = data_type
            field_schema.mode = 'nullable'
            table_schema.fields.append(field_schema)

        return table_schema
