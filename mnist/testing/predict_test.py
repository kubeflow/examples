"""Test mnist_client.

This file tests that we can send predictions to the model
using REST.

It is an integration test as it depends on having access to
a deployed model.

We use the pytest framework because
  1. It can output results in junit format for prow/gubernator
  2. It has good support for configuring tests using command line arguments
     (https://docs.pytest.org/en/latest/example/simple.html)

Python Path Requirements:
  kubeflow/testing/py - https://github.com/kubeflow/testing/tree/master/py
     * Provides utilities for testing

Manually running the test
 1. Configure your KUBECONFIG file to point to the desired cluster
"""

import json
import logging
import os
import requests
import six

from kubernetes.config import kube_config
from kubernetes import client as k8s_client

import pytest

from kubeflow.testing import util

def test_predict(master, namespace):
  app_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
  if app_credentials:
    print("Activate service account")
    util.run(["gcloud", "auth", "activate-service-account",
              "--key-file=" + app_credentials])

  if not master:
    print("--master set; using kubeconfig")
    # util.load_kube_config appears to hang on python3
    kube_config.load_kube_config()
    api_client = k8s_client.ApiClient()
    host = api_client.configuration.host
    print("host={0}".format(host))
    master = host.rsplit("/", 1)[-1]

  service = "mnist-service"
  token = util.run(["gcloud", "auth", "print-access-token"])
  if six.PY3 and hasattr(token, "decode"):
    token = token.decode()
  token = token.strip()

  headers = {
    "Authorization": "Bearer " + token,
  }

  this_dir = os.path.dirname(__file__)
  test_data = os.path.join(this_dir, "test_data", "instances.json")
  with open(test_data) as hf:
    instances = json.load(hf)

  # We proxy the request through the APIServer so that we can connect
  # from outside the cluster.
  url = ("https://{master}/api/v1/namespaces/{namespace}/services/{service}:8500"
         "/proxy/v1/models/mnist:predict").format(
           master=master, namespace=namespace, service=service)
  r = requests.post(url, json=instances, headers=headers, verify=False)

  if r.status_code == requests.codes.NOT_FOUND:
    message = "Request to {0} returned 404".format(url)
    logging.error(message)
    raise RuntimeError(message)

  if r.status_code != requests.codes.OK:
    msg = "Request to {0} exited with status code: {1} and content: {2}".format(
      url, r.status_code, r.content)
    logging.error(msg)
    raise RuntimeError(msg)

  result = json.loads(r.content)
  assert len(result["predictions"]) == 1
  predictions = result["predictions"][0]
  assert predictions.has_key("classes")
  assert predictions.has_key("predictions")
  assert len(predictions["predictions"]) == 10
  logging.info("URL %s returned; %s", url, r.content)

if __name__ == "__main__":
  pytest.main()
