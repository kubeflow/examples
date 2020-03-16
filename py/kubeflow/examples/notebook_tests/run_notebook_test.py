"""Runs notebook ipynb as test."""

import datetime
import logging
import os
import re
import uuid

import pytest

from kubeflow.examples.notebook_tests import nb_test_util
from kubeflow.testing import util

def test_run_notebook(record_xml_attribute, namespace, # pylint: disable=too-many-branches,too-many-statements
                      repos, image, notebook_path, gcs_test_path):
  notebook_name = os.path.basename(
      notebook_path).replace(".ipynb", "").replace("_", "-")
  junit_name = "_".join(["test", notebook_name])
  util.set_pytest_junit(record_xml_attribute, junit_name)

  name = "-".join([notebook_name,
                   datetime.datetime.now().strftime("%H%M%S"),
                   uuid.uuid4().hex[0:3]])

  util.set_pytest_junit(record_xml_attribute, junit_name)
  nb_test_util.run_papermill_job(notebook_path, name, namespace, repos, image)

  p = os.path.join(gcs_test_path, "artifacts", name)
  if not os.path.exists(p):
    try:
      os.makedirs(p)
    except Exception as e:
      logging.info("makedirs failed: %s", e)
  with open(os.path.join(p, "gg-test.txt"), "w") as f:
    f.write("GG TEST")

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO,
                      format=('%(levelname)s|%(asctime)s'
                              '|%(pathname)s|%(lineno)d| %(message)s'),
                      datefmt='%Y-%m-%dT%H:%M:%S',
                      )
  logging.getLogger().setLevel(logging.INFO)
  pytest.main()
