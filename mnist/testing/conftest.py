import pytest

def pytest_addoption(parser):
  parser.addoption(
      "--master", action="store", default="", help="IP address of GKE master")

  parser.addoption(
      "--namespace", action="store", default="", help="namespace of server")

@pytest.fixture
def master(request):
  return request.config.getoption("--master")

@pytest.fixture
def namespace(request):
  return request.config.getoption("--namespace")
