"""Some routines to setup the notebook.

This is separated out from util.py because this module installs some of the pip packages
that util depends on.
"""

import sys
import logging
import os
import subprocess
from importlib import reload

from pathlib import Path

FAIRING_PACKAGE = 'git+git://github.com/kubeflow/fairing.git@9b0d4ed4796ba349ac6067bbd802ff1d6454d015' # pylint: disable=line-too-long

TF_OPERATOR_COMMIT = "9238906"

def notebook_setup():
  # Install the SDK
  logging.basicConfig(format='%(message)s')
  logging.getLogger().setLevel(logging.INFO)

  home = str(Path.home())

  logging.info("pip installing fairing %s", FAIRING_PACKAGE)
  subprocess.check_call(["pip3", "install", "--user", FAIRING_PACKAGE])

  clone_dir = os.path.join(home, "git_tf-operator")
  if not os.path.exists(clone_dir):
    logging.info("Cloning the tf-operator repo")
    subprocess.check_call(["git", "clone", "https://github.com/kubeflow/tf-operator.git",
                           clone_dir])
  logging.info(f"Checkout kubeflow/tf-operator @{TF_OPERATOR_COMMIT}")
  subprocess.check_call(["git", "checkout", TF_OPERATOR_COMMIT], cwd=clone_dir)

  logging.info("pip installing fairing %s", FAIRING_PACKAGE)
  subprocess.check_call(["pip3", "install", "--user", FAIRING_PACKAGE])
      
  clone_dir = os.path.join(home, "git_tf-operator")
  if not os.path.exists(clone_dir):    
    logging.info("Cloning the tf-operator repo")
    subprocess.check_call(["git", "clone", "https://github.com/kubeflow/tf-operator.git",
                           clone_dir])
  logging.info(f"Checkout kubeflow/tf-operator @{TF_OPERATOR_COMMIT}")
  subprocess.check_call(["git", "checkout", TF_OPERATOR_COMMIT], cwd=clone_dir)    
  
  logging.info("Configure docker credentials")
  subprocess.check_call(["gcloud", "auth", "configure-docker", "--quiet"])
  if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    logging.info("Activating service account")
    subprocess.check_call(["gcloud", "auth", "activate-service-account",
                           "--key-file=" +
                           os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
                           "--quiet"])
  # Installing the python packages locally doesn't appear to have them automatically
  # added the path so we need to manually add the directory
  local_py_path = os.path.join(home, ".local/lib/python3.6/site-packages")
  tf_operator_py_path = os.path.join(clone_dir, "sdk/python")

  for p in [local_py_path, tf_operator_py_path]:
    if p not in sys.path:
      logging.info("Adding %s to python path", p)
      # Insert at front because we want to override any installed packages
      sys.path.insert(0, p)

  # Force a reload of kubeflow; since kubeflow is a multi namespace module
  # if we've loaded up some new kubeflow subpackages we need to force a reload to see them.
  import kubeflow
  reload(kubeflow)
