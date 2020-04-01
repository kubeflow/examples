import argparse
import tempfile
import logging
import os
import subprocess

logger = logging.getLogger(__name__)

from google.cloud import storage
from kubeflow.testing import util

def prepare_env():
  subprocess.check_call(["pip3", "install", "-Iv", "papermill==2.0.0"])
  subprocess.check_call(["pip3", "install", "-U", "nbconvert"])
  subprocess.check_call(["pip3", "install", "-U", "nbformat"])

def execute_notebook(notebook_path, parameters=None):
  import papermill #pylint: disable=import-error
  temp_dir = tempfile.mkdtemp()
  notebook_output_path = os.path.join(temp_dir, "out.ipynb")
  papermill.execute_notebook(notebook_path, notebook_output_path,
                             cwd=os.path.dirname(notebook_path),
                             parameters=parameters,
                             log_output=True)
  return notebook_output_path

def _upload_notebook_html(content, target):
  gcs_client = storage.Client()
  bucket_name, path = util.split_gcs_uri(target)

  bucket = gcs_client.get_bucket(bucket_name)

  logging.info("Uploading notebook to %s.", target)
  blob = bucket.blob(path)
  # Need to set content type so that if we browse in GCS we end up rendering
  # as html.
  blob.upload_from_string(content, content_type="text/html")

def run_notebook_test(notebook_path, parameters=None):
  import nbformat #pylint: disable=import-error
  import nbconvert #pylint: disable=import-error

  output_path = execute_notebook(notebook_path, parameters=parameters)

  with open(output_path, "r") as hf:
    actual_output = hf.read()

  nb = nbformat.reads(actual_output, as_version=4)
  html_exporter = nbconvert.HTMLExporter()
  (html_output, _) = html_exporter.from_notebook_node(nb)
  gcs_path = os.getenv("OUTPUT_GCS")
  _upload_notebook_html(html_output, gcs_path)

class NotebookExecutor:
  @staticmethod
  def test(notebook_path):
    """Test a notebook.

    Args:
      notebook_path: Absolute path of the notebook.
    """
    prepare_env()
    FILE_DIR = os.path.dirname(__file__)

    run_notebook_test(notebook_path)

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO,
                      format=('%(levelname)s|%(asctime)s'
                              '|%(message)s|%(pathname)s|%(lineno)d|'),
                      datefmt='%Y-%m-%dT%H:%M:%S',
                      )

  # fire isn't available in the notebook image which is why we aren't
  # using it.
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "--notebook_path", default="", type=str, help=("Path to the notebook"))

  args = parser.parse_args()

  NotebookExecutor.test(args.notebook_path)

