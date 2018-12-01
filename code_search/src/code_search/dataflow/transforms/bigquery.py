import apache_beam as beam
import apache_beam.io.gcp.bigquery as bigquery
import apache_beam.io.gcp.internal.clients as clients


# TODO(jlewi): Is this class necessary? Seems like a layer of indirection
# Around BigQuerySource. I think a better pattern might just be to create
# constants / classes defining the queries.
class BigQueryRead(beam.PTransform):
  """Wrapper over Apache Beam Big Query Read.

  This is an abstract class and one must override
  the `query_string` property to specify the query
  string.
  """

  def __init__(self, *args, **kw_args):
    super(BigQueryRead, self).__init__()

    self.read_args = args
    self.read_kw_args = kw_args

    # TODO(jlewi): We should handle the case where dataset and project
    # are set separately and table is not the full path "project:dataset.table"
    self._table = self.read_kw_args["table"]

    # Remove table from read_kw_args because it should not be passed to
    #
  @property
  def table(self):
    return self._table

  @property
  def limit(self):
    """Limit for the query rows.

    The case None should be handled if using
    this property.
    """
    return None

  @property
  def query_string(self):
    raise NotImplementedError

  def expand(self, input_or_inputs):
    self.read_kw_args["query"] = self.query_string
    self.read_kw_args["use_standard_sql"] = True

    return (input_or_inputs
      | beam.io.Read(beam.io.BigQuerySource(*self.read_args,
                                            **self.read_kw_args))
    )


class BigQuerySchema(object):
  """Class for representing BigQuery schemas."""

  def __init__(self, columns):
    """Construct the schema.

    Args: list of tuples defining the BigQuerySchema [
      ('column_name', 'column_type')
    ]
    """
    self.columns = columns

    self.table_schema = clients.bigquery.TableSchema()

    for column_name, column_type in self.columns:
      field_schema = clients.bigquery.TableFieldSchema()
      field_schema.name = column_name
      field_schema.type = column_type
      field_schema.mode = 'nullable'
      self.table_schema.fields.append(field_schema)

# TODO(https://github.com/kubeflow/examples/issues/381):
# We should probably refactor this into a separate
# class for helping with schemas and not bundle that with the BigQuerySink.
class BigQueryWrite(beam.PTransform):
  """Wrapper over Apache Beam BigQuery Write.

  This is an abstract class and one must override
  the `column_list` property for valid write transform.
  This property should return a list of tuples as
    [
      ('column_name', 'column_type')
    ]
  """

  def __init__(self, batch_size=500, *args, **kw_args):
    super(BigQueryWrite, self).__init__(*args, **kw_args)

    self.batch_size = batch_size
    self.write_args = args
    self.write_kw_args = kw_args
  @property
  def column_list(self):
    raise NotImplementedError

  @property
  def output_schema(self):
    return self.construct_schema(self.column_list)

  def expand(self, input_or_inputs):
    self.write_kw_args["schema"] = self.output_schema
    return (input_or_inputs
      | beam.io.WriteToBigQuery(*self.write_args, **self.write_kw_args)
    )

  @staticmethod
  def construct_schema(column_list):
    table_schema = clients.bigquery.TableSchema()

    for column_name, column_type in column_list:
      field_schema = clients.bigquery.TableFieldSchema()
      field_schema.name = column_name
      field_schema.type = column_type
      field_schema.mode = 'nullable'
      table_schema.fields.append(field_schema)

    return table_schema
