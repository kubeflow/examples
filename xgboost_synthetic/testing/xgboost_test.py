import argparse
import logging
import os
import subprocess
import time

from kubeflow.testing import util

def create_job(args, app_dir): #pylint:disable=redefined-outer-name
  '''Generate Job and summit.'''
  util.run(['gcloud', 'auth', 'activate-service-account',
          "--key-file=/secret/gcp-credentials/key.json"], cwd=app_dir)
  util.run(['gcloud', '--project=kubeflow-ci-deployment', 'container',
          "clusters", "get-credentials", "--zone=us-east1-b", args.cluster], cwd=app_dir)

  configmap = 'xgb-notebooks-tests'
  util.run(['kustomize', 'edit', 'add', 'configmap', configmap,
          '--from-literal=name=' + args.name], cwd=app_dir)
  util.run(['kustomize', 'edit', 'add', 'configmap', configmap,
          '--from-literal=pullNumber=' + args.pullNumber], cwd=app_dir)
  util.run(['kustomize', 'edit', 'set', 'namespace', args.namespace], cwd=app_dir)
  util.run(['kustomize', 'edit', 'set', 'image', 'execute-image=' + args.image], cwd=app_dir)
  util.run(['kustomize', 'build', app_dir, '-o', 'generated.yaml'], cwd=app_dir)
  util.run(['kubectl', 'apply', '-f', 'generated.yaml'], cwd=app_dir)
  logging.info("Created deployment %s in namespaces %s", args.name, args.namespace)

def get_pod_logs(name, namespace, app_dir): #pylint:disable=redefined-outer-name
  '''Cannot get logs by k8s python api, using kubectl command to get logs.'''
  logging.info("Getting pod %s logs...", name)
  util.run(['kubectl', 'logs', name, '-n', namespace], cwd=app_dir)

def check_job_status(namespace, app_dir): #pylint:disable=redefined-outer-name
  '''Cannot get job by k8s python api, using kubectl command to check job status.'''
  is_successed = False
  pod_info, pod_name, pod_status = '', '', ''
  for _ in range(0, 30):
    time.sleep(60)
    subCmd = "kubectl get pod -n " + namespace + " | grep -m1 xgboost-test"
    pod_info = subprocess.run(subCmd,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              shell=True,
                              universal_newlines=True)
    if len(str(pod_info.stdout).split()) >= 2:
      pod_name = str(pod_info.stdout).split()[0]
      pod_status = str(pod_info.stdout).split()[2]

    if pod_name:
      if pod_status == "Pending":
        logging.info("Pod %s is Pending.", pod_name)
      elif pod_status == "Running":
        logging.info("Pod %s is Running.", pod_name)
      elif pod_status == "Completed":
        logging.info("Pod %s is Completed.", pod_name)
        get_pod_logs(pod_name, namespace, app_dir)
        is_successed = True
        break
      elif pod_status == "Error":
        get_pod_logs(pod_name, namespace, app_dir)
        raise RuntimeError("Failed to execute notebook.")
      else:
        logging.warning("Pod %s status %s.", pod_name, pod_status)
    else:
      logging.warning("Cannot get the pod name, retry after 60 seconds.")

  if not is_successed:
    raise RuntimeError("Timeout to get the executing notebook pod after 30 munites.")


if __name__ == "__main__":

  logging.basicConfig(level=logging.INFO)

  parser = argparse.ArgumentParser()
  parser.add_argument(
    "--name", help="deploy application name", type=str, required=True)
  parser.add_argument(
    "--namespace", help="The namespace for the application", type=str, required=True)
  parser.add_argument(
    "--image", help="Image name for the application", type=str, required=True)
  parser.add_argument(
    "--pullNumber", help="The PR number", type=str, required=True)
  parser.add_argument(
    "--cluster", help="The cluster which the applition running in", type=str, required=True)

  app_dir = os.path.dirname(__file__)
  app_dir = os.path.abspath(app_dir)

  args = parser.parse_args()
  create_job(args, app_dir)
  check_job_status(args.namespace, app_dir)
