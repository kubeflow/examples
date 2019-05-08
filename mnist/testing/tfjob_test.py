"""Test training using TFJob.

This file tests that we can submit the job
and that the job runs to completion.

It is an integration test as it depends on having access to
a Kubeflow deployment to submit the TFJob to.

Python Path Requirements:
  kubeflow/tf-operator/py - https://github.com/kubeflow/tf-operator
     * Provides utilities for testing TFJobs
  kubeflow/testing/py - https://github.com/kubeflow/testing/tree/master/py
     * Provides utilities for testing

Manually running the test
 1. Configure your KUBECONFIG file to point to the desired cluster
 2. Set --params=name=${NAME},namespace=${NAMESPACE}
    * name should be the name for your job
    * namespace should be the namespace to use
 3. To test a new image set the parameter image e.g
     --params=name=${NAME},namespace=${NAMESPACE},image=${IMAGE}
 4. To control how long it trains set sample_size and num_epochs
     --params=trainSteps=10,batchSize=10,...
"""

import json
import logging
import os
import subprocess

from kubernetes import client as k8s_client
from kubeflow.tf_operator import tf_job_client #pylint: disable=no-name-in-module
from kubeflow.tf_operator import test_runner #pylint: disable=no-name-in-module

from kubeflow.testing import test_util
from kubeflow.testing import util

class TFJobTest(test_util.TestCase):
  def __init__(self, args):
    namespace, name, env = test_runner.parse_runtime_params(args)
    self.app_dir = args.app_dir

    if not self.app_dir:
      self.app_dir = os.path.join(os.path.dirname(__file__), "..",
                                  "training/GCS")
      self.app_dir = os.path.abspath(self.app_dir)
      logging.info("--app_dir not set defaulting to: %s", self.app_dir)

    self.env = env
    self.namespace = namespace
    self.params = args.params
    super(TFJobTest, self).__init__(class_name="TFJobTest", name=name)

  def test_train(self):
    # We repeat the test multiple times.
    # This ensures that if we delete the job we can create a new job with the
    # same name.
    api_client = k8s_client.ApiClient()

    # TODO (jinchihe) beflow code will be removed once new test-worker image
    # is publish in https://github.com/kubeflow/testing/issues/373.
    kusUrl = 'https://github.com/kubernetes-sigs/kustomize/' \
         'releases/download/v2.0.3/kustomize_2.0.3_linux_amd64'
    util.run(['wget', '-O', '/usr/local/bin/kustomize', kusUrl], cwd=self.app_dir)
    util.run(['chmod', 'a+x', '/usr/local/bin/kustomize'], cwd=self.app_dir)

    # Setup parameters for kustomize
    configmap = 'mnist-map-training'
    for pair in self.params.split(","):
      k, v = pair.split("=", 1)
      if k == "namespace":
        util.run(['kustomize', 'edit', 'set', k, v], cwd=self.app_dir)
      elif k == "image":
        util.run(['kustomize', 'edit', 'set', k, 'training-image=' + v], cwd=self.app_dir)
      elif k == "numPs":
        util.run(['../base/definition.sh', '--numPs', v], cwd=self.app_dir)
      elif k == "numWorkers":
        util.run(['../base/definition.sh', '--numWorkers', v], cwd=self.app_dir)
      elif k == "secret":
        secretName, secretMountPath = v.split("=", 1)
        util.run(['kustomize', 'edit', 'add', 'configmap', configmap,
                '--from-literal=secretName=' + secretName], cwd=self.app_dir)
        util.run(['kustomize', 'edit', 'add', 'configmap', configmap,
                '--from-literal=secretMountPath=' + secretMountPath], cwd=self.app_dir)
      elif k == "envVariables":
        var_k, var_v = v.split("=", 1)
        util.run(['kustomize', 'edit', 'add', 'configmap', configmap,
                '--from-literal=' + var_k + '=' + var_v], cwd=self.app_dir)
      else:
        util.run(['kustomize', 'edit', 'add', 'configmap', configmap,
                '--from-literal=' + k + '=' + v], cwd=self.app_dir)

    # Create the TF job
    # Seems the util.run cannot handle pipes case, using check_call.
    subCmd = 'kustomize build ' + self.app_dir + '| kubectl apply -f -'
    subprocess.check_call(subCmd, shell=True)
    logging.info("Created job %s in namespaces %s", self.name, self.namespace)

    # Wait for the job to complete.
    logging.info("Waiting for job to finish.")
    results = tf_job_client.wait_for_job(
          api_client,
          self.namespace,
          self.name,
          status_callback=tf_job_client.log_status)
    logging.info("Final TFJob:\n %s", json.dumps(results, indent=2))

    # Check for errors creating pods and services. Can potentially
    # help debug failed test runs.
    creation_failures = tf_job_client.get_creation_failures_from_tfjob(
        api_client, self.namespace, results)
    if creation_failures:
      logging.warning(creation_failures)

    if not tf_job_client.job_succeeded(results):
      self.failure = "Job {0} in namespace {1} in status {2}".format(  # pylint: disable=attribute-defined-outside-init
          self.name, self.namespace, results.get("status", {}))
      logging.error(self.failure)

      # if the TFJob failed, print out the pod logs for debugging.
      pod_names = tf_job_client.get_pod_names(
          api_client, self.namespace, self.name)
      logging.info("The Pods name:\n %s", pod_names)

      core_api = k8s_client.CoreV1Api(api_client)

      for pod in pod_names:
        logging.info("Getting logs of Pod %s.", pod)
        try:
          pod_logs = core_api.read_namespaced_pod_log(pod, self.namespace)
          logging.info("The logs of Pod %s log:\n %s", pod, pod_logs)
        except k8s_client.rest.ApiException as e:
          logging.info("Exception when calling CoreV1Api->read_namespaced_pod_log: %s\n", e)
      return

    # We don't delete the jobs. We rely on TTLSecondsAfterFinished
    # to delete old jobs. Leaving jobs around should make it
    # easier to debug.

if __name__ == "__main__":
  test_runner.main(module=__name__)
