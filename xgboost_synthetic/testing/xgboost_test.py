import datetime
import logging
import os
import time
import uuid
import yaml

import pytest

from kubernetes import client as k8s_client
from kubernetes.client import rest
from kubeflow.testing import util

# TODO(jlewi): This test is currently failing because various things
# need to be updated to work with 0.7.0. Until that's fixed we mark it
# as expected to fail so we can begin to get signal.
@pytest.mark.xfail
def test_xgboost_synthetic(record_xml_attribute, name, namespace, cluster, # pylint: disable=too-many-branches,too-many-statements
                           repos, image, app_dir):
  '''Generate Job and summit.'''
  util.set_pytest_junit(record_xml_attribute, "test_xgboost_synthetic")
  app_dir = os.path.abspath(app_dir)

  if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    util.run(['gcloud', 'auth', 'activate-service-account',
            "--key-file=" + os.getenv("GOOGLE_APPLICATION_CREDENTIALS")],
             cwd=app_dir)

  # TODO(jlewi): We should just assume that kubeconfig has been set.
  if cluster:
    util.run(['gcloud', '--project=kubeflow-ci-deployment', 'container',
              "clusters", "get-credentials", "--zone=us-east1-b", cluster],
               cwd=app_dir)

  with open("job.yaml") as hf:
    job = yaml.load(hf)

  job["metadata"]["namespace"] = name
  job["metadata"]["namespace"] = namespace

  # We need to checkout the correct version of the code
  # in presubmits and postsubmits. We should check the environment variables
  # for the prow environment variables to get the appropriate values.
  # We should probably also only do that if the
  # See
  # https://github.com/kubernetes/test-infra/blob/45246b09ed105698aa8fb928b7736d14480def29/prow/jobs.md#job-environment-variables
  if not repos:
    version = "@HEAD"
    if os.getenv("PULL_NUMBER"):
      version = "@{0}:{1}".format(os.getenv("PULL_PULL_SHA"),
                                  os.getenv("PULL_NUMBER"))

    else:
      if os.getenv("PULL_BASE_SHA"):
        version = "@{0}".format(os.getenv("PULL_BASE_SHA"))

    repos = "kubeflow/examples" + version

  logging.info("Repos set to %s", repos)
  job["spec"]["template"]["spec"]["initContainers"][0]["command"] = [
    "/usr/local/bin/checkout_repos.sh",
    "--repos=" + repos,
    "--src_dir=/src",
    "--depth=all",
  ]
  job["spec"]["template"]["spec"]["containers"][0]["image"] = image
  util.load_kube_config(persist_config=False)

  if name:
    job["metadata"]["name"] = name
  else:
    job["metadata"]["name"] = ("xgboost-test-" +
                               datetime.datetime.now().strftime("%H%M%S")
                               + "-" + uuid.uuid4().hex[0:3])

  # Create an API client object to talk to the K8s master.
  api_client = k8s_client.ApiClient()
  batch_api = k8s_client.BatchV1Api(api_client)

  logging.info("Creating job:\n%s", yaml.dump(job))
  batch_api.create_namespaced_job(job["metadata"]["namespace"], job)
  logging.info("Created job %s in namespaces %s", name, namespace)

  # Wait for tiller to be ready
  end_time = datetime.datetime.now() + datetime.timedelta(
    minutes=15)

  namespace = job["metadata"]["namespace"]
  name = job["metadata"]["name"]
  last_condition = None
  while datetime.datetime.now() < end_time:
    try:
      job = batch_api.read_namespaced_job(name, namespace)
    except rest.ApiException as e:
      logging.error("There was a problem getting job %s.%s; %s",
                    namespace, name, e)
      time.sleep(10)
      continue
    # ready_replicas could be None
    if not job.conditions:
      logging.info("Job missing condition")

    last_condition = job.conditions[-1]
    if last_condition["type"] in ["Failed", "Complete"]:
      break
    logging.info("Waiting for job %s.%s", namespace, name)
    time.sleep(10)

  logging.info("Final Job spec:\n%s", yaml.safe_dump(job))
  util.run(["kubectl", "describe", "job", "-n", namespace, name])

  if not last_condition or last_condition["type"] not in ["Failed", "Complete"]:
    logging.error("Timeout waiting for job %s.%s to finish.", namespace, name)
    assert last_condition["type"] in ["Failed", "Complete"]
  else:
    assert last_condition["type"] == "Complete"

if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO,
                      format=('%(levelname)s|%(asctime)s'
                              '|%(pathname)s|%(lineno)d| %(message)s'),
                      datefmt='%Y-%m-%dT%H:%M:%S',
                      )
  logging.getLogger().setLevel(logging.INFO)
  pytest.main()
