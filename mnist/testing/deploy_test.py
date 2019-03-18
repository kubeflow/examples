"""Test deploying the mnist model.

This file tests that we can deploy the model.

It is an integration test as it depends on having access to
a Kubeflow deployment to deploy on. It also depends on having a model.

Python Path Requirements:
  kubeflow/testing/py - https://github.com/kubeflow/testing/tree/master/py
     * Provides utilities for testing

Manually running the test
 1. Configure your KUBECONFIG file to point to the desired cluster
 2. Set --params=name=${NAME},namespace=${NAMESPACE}
    * name should be the name for your job
    * namespace should be the namespace to use
 3. Use the modelBasePath parameter to the model to test.
     --params=...,modelBasePath=${MODEL_BASE_PATH}

"""

import logging
import os

from kubernetes import client as k8s_client
from kubeflow.tf_operator import test_runner #pylint: disable=no-name-in-module

from kubeflow.testing import ks_util
from kubeflow.testing import test_util
from kubeflow.testing import util

# TODO(jlewi): Should we refactor this to use pytest like predict_test
# and not depend on test_runner.
class MnistDeployTest(test_util.TestCase):
  def __init__(self, args):
    namespace, name, env = test_runner.parse_runtime_params(args)
    self.app_dir = args.app_dir

    if not self.app_dir:
      self.app_dir = os.path.join(os.path.dirname(__file__), "..",
                                  "ks_app")
      self.app_dir = os.path.abspath(self.app_dir)
      logging.info("--app_dir not set defaulting to: %s", self.app_dir)

    self.env = env
    self.namespace = namespace
    self.params = args.params
    self.ks_cmd = ks_util.get_ksonnet_cmd(self.app_dir)
    super(MnistDeployTest, self).__init__(class_name="MnistDeployTest",
                                          name=name)

  def test_serve(self):
    # We repeat the test multiple times.
    # This ensures that if we delete the job we can create a new job with the
    # same name.
    api_client = k8s_client.ApiClient()

    # Apply the components
    for component in ["mnist-deploy-gcp", "mnist-service"]:
      # Setup the ksonnet app
      ks_util.setup_ks_app(self.app_dir, self.env, self.namespace, component,
                           self.params)

      util.run([self.ks_cmd, "apply", self.env, "-c", component],
               cwd=self.app_dir)

      logging.info("Created deployment %s in namespaces %s", self.name, self.namespace)

    util.wait_for_deployment(api_client, self.namespace, self.name,
                             timeout_minutes=4)

    # We don't delete the resources. We depend on the namespace being
    # garbage collected.

if __name__ == "__main__":
  # TODO(jlewi): It looks like using test_runner we don't exit with an error
  # if the deployment doesn't succeed. So the Argo workflow continues which
  # isn't what we want. Might be a good reason to switch to using
  # pytest.
  test_runner.main(module=__name__)
