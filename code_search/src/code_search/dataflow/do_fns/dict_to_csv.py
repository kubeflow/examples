import csv
import io
import apache_beam as beam


class DictToCSVString(beam.DoFn):
  """Convert incoming dict to a CSV string.

  The input element must be a dict and
  values must be string-serializable.
    {
      "key1": "STRING",
      "key2": "STRING"
    }
  """
  def __init__(self, fieldnames):
    super(DictToCSVString, self).__init__()

    self.fieldnames = fieldnames

  def process(self, element, *_args, **_kwargs):
    fieldnames = self.fieldnames
    filtered_element = {
      key: value.encode('utf-8')
      for (key, value) in element.iteritems()
      if key in fieldnames
    }
    with io.BytesIO() as stream:
      writer = csv.DictWriter(stream, fieldnames)
      writer.writerow(filtered_element)
      csv_string = stream.getvalue().strip('\r\n')

    yield csv_string
