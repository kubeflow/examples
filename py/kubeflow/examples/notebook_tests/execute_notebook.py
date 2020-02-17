import fire
import tempfile
import logging
import os
import subprocess

logger = logging.getLogger(__name__)

def prepare_env():
  subprocess.check_call(["pip3", "install", "-U", "papermill"])
  subprocess.check_call(["pip3", "install", "-r", "../requirements.txt"])


def execute_notebook(notebook_path, parameters=None):
  import papermill #pylint: disable=import-error
  temp_dir = tempfile.mkdtemp()
  notebook_output_path = os.path.join(temp_dir, "out.ipynb")
  papermill.execute_notebook(notebook_path, notebook_output_path,
                             cwd=os.path.dirname(notebook_path),
                             parameters=parameters,
                             log_output=True)
  return notebook_output_path

def run_notebook_test(notebook_path, expected_messages, parameters=None):
  output_path = execute_notebook(notebook_path, parameters=parameters)
  actual_output = open(output_path, 'r').read()
  for expected_message in expected_messages:
    if not expected_message in actual_output:
      logger.error(actual_output)
      assert False, "Unable to find from output: " + expected_message

class NotebookExecutor:
  @staticmethod
  def test(notebook_path):
    """Test a notebook.

    Args:
      notebook_path: Absolute path of the notebook.
    """
    prepare_env()
    FILE_DIR = os.path.dirname(__file__)

    EXPECTED_MGS = [
        "Finished upload of",
        "Model export success: mockup-model.dat",
        "Pod started running True",
        "Cluster endpoint: http:",
    ]
    run_notebook_test(notebook_path, EXPECTED_MGS)

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO,
                      format=('%(levelname)s|%(asctime)s'
                              '|%(message)s|%(pathname)s|%(lineno)d|'),
                      datefmt='%Y-%m-%dT%H:%M:%S',
                      )

  fire.Fire(NotebookExecutor)
