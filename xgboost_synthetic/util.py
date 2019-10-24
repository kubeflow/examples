import sys
import logging
import os
import shutil
import subprocess
import json
import requests

from pathlib import Path

from retrying import retry
import numpy as np

KFP_PACKAGE = 'https://storage.googleapis.com/ml-pipeline/release/0.1.32/kfp.tar.gz'
FAIRING_PACKAGE = 'git+git://github.com/kubeflow/fairing.git@7c93e888c3fc98bdf5fb0140e90f6407ce7a807b'

def notebook_setup():
  # Install the SDK
  logging.basicConfig(format='%(message)s')
  logging.getLogger().setLevel(logging.INFO)

  logging.info("pip installing requirements.txt")
  subprocess.check_call(["pip3", "install", "--user", "-r", "requirements.txt"])
  logging.info("pip installing KFP %s", KFP_PACKAGE)
  subprocess.check_call(["pip3", "install", "--user", KFP_PACKAGE, "--upgrade"])
  logging.info("pip installing fairing %s", FAIRING_PACKAGE)
  subprocess.check_call(["pip3", "install", "--user", FAIRING_PACKAGE])

  logging.info("Configure docker credentials")
  subprocess.check_call(["gcloud", "auth", "configure-docker", "--quiet"])
  if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    logging.info("Activating service account")
    subprocess.check_call(["gcloud", "auth", "activate-service-account",
                           "--key-file=" +
                           os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
                           "--quiet"])
      
  home = str(Path.home())

  # Installing the python packages locally doesn't appear to have them automatically
  # added the path so we need to manually add the directory
  local_py_path = os.path.join(home, ".local/lib/python3.6/site-packages")
  if not local_py_path in sys.path:
    logging.info("Adding %s to python path", local_py_path)
    # Insert at front because we want to override any installed packages 
    sys.path.insert(0, local_py_path)

def copy_data_to_nfs(nfs_path, model_dir):
  if not os.path.exists(nfs_path):
    shutil.copytree("ames_dataset", nfs_path)

  if not os.path.exists(model_dir):
    os.makedirs(model_dir)

@retry(wait_exponential_multiplier=1000, wait_exponential_max=5000,
       stop_max_delay=2*60*1000)
def predict_nparray(url, data, feature_names=None):
  pdata = {
      "data": {
          "names":feature_names,
          "tensor": {
              "shape": np.asarray(data.shape).tolist(),
              "values": data.flatten().tolist(),
          },
      }
  }
  serialized_data = json.dumps(pdata)
  r = requests.post(url, data={'json':serialized_data}, timeout=5)
  return r
