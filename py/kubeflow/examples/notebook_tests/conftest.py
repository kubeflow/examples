import pytest

def pytest_addoption(parser):
  parser.addoption(
    "--name", help="Name for the job. If not specified one was created "
    "automatically", type=str, default="")
  parser.addoption(
    "--namespace", help=("The namespace to run in. This should correspond to"
                         "a namespace associated with a Kubeflow namespace."),
                   type=str,
    default="kubeflow-kf-ci-v1-user")
  parser.addoption(
    "--image", help="Notebook image to use", type=str,
    default="gcr.io/kubeflow-images-public/"
            "tensorflow-1.15.2-notebook-cpu:1.0.0")
  parser.addoption(
    "--repos", help="The repos to checkout; leave blank to use defaults",
    type=str, default="")
  parser.addoption(
    "--notebook_path", help=("Path to the testing notebook file, starting from"
                             "the base directory of examples repository."),
    type=str, default="")
  parser.addoption(
    "--test-target-name", help=("Test target name, used as junit class name."),
    type=str, default="")
  parser.addoption(
    "--artifacts-gcs", help=("GCS to upload artifacts to."),
    type=str, default="")

@pytest.fixture
def name(request):
  return request.config.getoption("--name")

@pytest.fixture
def namespace(request):
  return request.config.getoption("--namespace")

@pytest.fixture
def image(request):
  return request.config.getoption("--image")

@pytest.fixture
def repos(request):
  return request.config.getoption("--repos")

@pytest.fixture
def notebook_path(request):
  return request.config.getoption("--notebook_path")

@pytest.fixture
def test_target_name(request):
  return request.config.getoption("--test-target-name")

@pytest.fixture
def artifacts_gcs(request):
  return request.config.getoption("--artifacts-gcs")
