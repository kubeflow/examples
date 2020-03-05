"""Some utitilies for running notebook tests."""

import datetime
import logging
import os
from urllib.parse import urlencode
import uuid
import yaml

from google.cloud import storage
from kubernetes import client as k8s_client
from kubeflow.testing import argo_build_util
from kubeflow.testing import prow_artifacts
from kubeflow.testing import util

# This is the bucket where the batch jobs will uploaded an HTML version of the
# notebook will be written to. The K8s job is running in a Kubeflow cluster
# so it needs to be a bucket that the kubeflow cluster can write to.
# This is why we don't write directly to the bucket used for prow artifacts
NB_BUCKET = "kubeflow-ci-deployment"
PROJECT = "kbueflow-ci-deployment"

def logs_for_job(project, job_name):
  """Get a stack driver link for the job with the specified name."""
  logs_filter = f"""resource.type="k8s_container"
   labels."k8s-pod/job-name" = "{job_name}"
"""

  new_params = {"project": project,
                # Logs for last 7 days
                "interval": 'P7D',
                "advancedFilter": logs_filter}

  query = urlencode(new_params)

  url = "https://console.cloud.google.com/logs/viewer?" + query

  return url

def run_papermill_job(notebook_path, name, namespace, # pylint: disable=too-many-branches,too-many-statements
                      repos, image, artifacts_gcs="", test_target_name=""):
  """Generate a K8s job to run a notebook using papermill

  Args:
    notebook_path: Path to the notebook. This should be in the form
      "{REPO_OWNER}/{REPO}/path/to/notebook.ipynb"
    name: Name for the K8s job
    namespace: The namespace where the job should run.
    repos: Which repos to checkout; if None or empty tries
      to infer based on PROW environment variables
    image: The docker image to run the notebook in.
  """

  util.maybe_activate_service_account()

  with open("job.yaml") as hf:
    job = yaml.load(hf)

  if notebook_path.startswith("/"):
    raise ValueError("notebook_path={0} should not start with /".format(
      notebook_path))

  # We need to checkout the correct version of the code
  # in presubmits and postsubmits. We should check the environment variables
  # for the prow environment variables to get the appropriate values.
  # We should probably also only do that if the
  # See
  # https://github.com/kubernetes/test-infra/blob/45246b09ed105698aa8fb928b7736d14480def29/prow/jobs.md#job-environment-variables
  if not repos:
    repos = argo_build_util.get_repo_from_prow_env()
    logging.info(f"Using repos {repos}")

  if not repos:
    raise ValueError("Could not get repos from prow environment variable "
                     "and --repos isn't explicitly set")

  repos += ",kubeflow/testing@HEAD"

  logging.info("Repos set to %s", repos)
  job["spec"]["template"]["spec"]["initContainers"][0]["command"] = [
    "/usr/local/bin/checkout_repos.sh",
    "--repos=" + repos,
    "--src_dir=/src",
    "--depth=all",
  ]

  job["spec"]["template"]["spec"]["containers"][0]["image"] = image

  full_notebook_path = os.path.join("/src", notebook_path)
  job["spec"]["template"]["spec"]["containers"][0]["command"] = [
    "python3", "-m",
    "kubeflow.examples.notebook_tests.execute_notebook",
    "--notebook_path", full_notebook_path]

  job["spec"]["template"]["spec"]["containers"][0][
    "workingDir"] = os.path.dirname(full_notebook_path)

  # The prow bucket to use for results/artifacts
  prow_bucket = prow_artifacts.PROW_RESULTS_BUCKET

  if artifacts_gcs:
    prow_dir = os.path.join(artifacts_gcs, "artifacts")
    if test_target_name:
      prow_dir = os.path.join(prow_dir, test_target_name)
    logging.info("Prow artifacts directory: %s", prow_dir)
    prow_bucket, prow_path = util.split_gcs_uri(prow_dir)
  elif os.getenv("REPO_OWNER") and os.getenv("REPO_NAME"):
    # Running under prow
    prow_dir = prow_artifacts.get_gcs_dir(prow_bucket)
    logging.info("Prow artifacts dir: %s", prow_dir)
    prow_dir = os.path.join(prow_dir, "artifacts")

    if os.getenv("TEST_TARGET_NAME"):
      prow_dir = os.path.join(
        prow_dir, os.getenv("TEST_TARGET_NAME").lstrip("/"))
    prow_bucket, prow_path = util.split_gcs_uri(prow_dir)

  else:
    prow_path = "notebook-test" + datetime.datetime.now().strftime("%H%M%S")
    prow_path = prow_path + "-" + uuid.uuid4().hex[0:3]
    prow_dir = util.to_gcs_uri(prow_bucket, prow_path)

  prow_path = os.path.join(prow_path, name + ".html")
  output_gcs = util.to_gcs_uri(NB_BUCKET, prow_path)

  job["spec"]["template"]["spec"]["containers"][0]["env"] = [
    {"name": "OUTPUT_GCS", "value": output_gcs},
    {"name": "PYTHONPATH",
     "value": "/src/kubeflow/testing/py:/src/kubeflow/examples/py"},
  ]

  logging.info("Notebook will be written to %s", output_gcs)
  util.load_kube_config(persist_config=False)

  if name:
    job["metadata"]["name"] = name
  else:
    job["metadata"]["name"] = ("notebook-test-" +
                               datetime.datetime.now().strftime("%H%M%S")
                               + "-" + uuid.uuid4().hex[0:3])
  name = job["metadata"]["name"]

  job["metadata"]["namespace"] = namespace

  # Create an API client object to talk to the K8s master.
  api_client = k8s_client.ApiClient()
  batch_api = k8s_client.BatchV1Api(api_client)

  logging.info("Creating job:\n%s", yaml.dump(job))
  actual_job = batch_api.create_namespaced_job(job["metadata"]["namespace"],
                                               job)
  logging.info("Created job %s.%s:\n%s", namespace, name,
               yaml.safe_dump(actual_job.to_dict()))

  logging.info("*********************Job logs************************")
  logging.info(logs_for_job(PROJECT, name))
  logging.info("*****************************************************")
  final_job = util.wait_for_job(api_client, namespace, name,
                                timeout=datetime.timedelta(minutes=30))

  logging.info("Final job:\n%s", yaml.safe_dump(final_job.to_dict()))

  logging.info("*********************Job logs************************")
  logging.info(logs_for_job(PROJECT, name))
  logging.info("*****************************************************")

  # Download notebook html to artifacts
  logging.info("Copying %s to bucket %s", output_gcs, prow_bucket)

  storage_client = storage.Client()
  bucket = storage_client.get_bucket(NB_BUCKET)
  blob = bucket.get_blob(prow_path)

  destination_bucket = storage_client.get_bucket(prow_bucket)
  bucket.copy_blob(blob, destination_bucket)

  if not final_job.status.conditions:
    raise RuntimeError("Job {0}.{1}; did not complete".format(namespace, name))

  last_condition = final_job.status.conditions[-1]

  if last_condition.type not in ["Complete"]:
    logging.error("Job didn't complete successfully")
    raise RuntimeError("Job {0}.{1} failed".format(namespace, name))
