import logging
import os

import pytest

from kubeflow.examples.notebook_tests import nb_test_util
from kubeflow.testing import util

# TODO(jlewi): This test is new; there's some work to be done to make it
# reliable. So for now we mark it as expected to fail in presubmits
# We only mark it as expected to fail
# on presubmits because if expected failures don't show up in test grid
# and we want signal in postsubmits and periodics
@pytest.mark.xfail(os.getenv("JOB_TYPE") == "presubmit", reason="Flaky")
def test_mnist_gcp(record_xml_attribute, name, namespace, # pylint: disable=too-many-branches,too-many-statements
                   repos, image):
  '''Generate Job and summit.'''
  util.set_pytest_junit(record_xml_attribute, "test_mnist_gcp")
  nb_test_util.run_papermill_job(name, namespace, repos, image)


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO,
                      format=('%(levelname)s|%(asctime)s'
                              '|%(pathname)s|%(lineno)d| %(message)s'),
                      datefmt='%Y-%m-%dT%H:%M:%S',
                      )
  logging.getLogger().setLevel(logging.INFO)
  pytest.main()
