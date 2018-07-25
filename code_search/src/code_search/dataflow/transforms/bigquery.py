import apache_beam as beam
import apache_beam.io.gcp.bigquery as bigquery
import apache_beam.io.gcp.internal.clients as clients


class BigQueryRead(beam.PTransform):
  """Wrapper over Apache Beam Big Query Read.

  This is an abstract class and one must override
  the `query_string` property to specify the query
  string.
  """

  def __init__(self, project, dataset=None, table=None):
    super(BigQueryRead, self).__init__()

    self.project = project
    self.dataset = dataset
    self.table = table

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
    return (input_or_inputs
      | beam.io.Read(beam.io.BigQuerySource(project=self.project,
                                            query=self.query_string,
                                            use_standard_sql=True))
    )


class BigQueryWrite(beam.PTransform):
  """Wrapper over Apache Beam BigQuery Write.

  This is an abstract class and one must override
  the `column_list` property for valid write transform.
  This property should return a list of tuples as
    [
      ('column_name', 'column_type')
    ]
  """

  def __init__(self, project, dataset, table, batch_size=500,
               write_disposition=bigquery.BigQueryDisposition.WRITE_TRUNCATE):
    super(BigQueryWrite, self).__init__()

    self.project = project
    self.dataset = dataset
    self.table = table
    self.write_disposition = write_disposition
    self.batch_size = batch_size

  @property
  def column_list(self):
    raise NotImplementedError

  @property
  def output_schema(self):
    return self.construct_schema(self.column_list)

  def expand(self, input_or_inputs):
    return (input_or_inputs
      | beam.io.WriteToBigQuery(project=self.project,
                                dataset=self.dataset,
                                table=self.table,
                                schema=self.output_schema,
                                batch_size=self.batch_size,
                                write_disposition=self.write_disposition)
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
