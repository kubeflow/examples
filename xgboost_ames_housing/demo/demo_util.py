import os
import shutil
import subprocess

KFP_PACKAGE = 'https://storage.googleapis.com/ml-pipeline/release/0.1.20/kfp.tar.gz'
def notebook_setup(path_to_fairing):
    # Install some pip pckages
    # Install the SDK
    for p in ["joblib", "sklearn", "fire", "retrying"]:
        subprocess.check_call(["pip3", "install", p])

    subprocess.check_call(["pip3", "install", KFP_PACKAGE, "--upgrade"])

    # Override fairing path; 
    # do this before importing anything else
    import logging
    import os
    from pathlib import Path
    import sys

    if os.path.exists(path_to_fairing):    
        logging.info("Adding %s to path", path_to_fairing)
        sys.path = [path_to_fairing] + sys.path
    
    logging.basicConfig(format='%(message)s')
    logging.getLogger().setLevel(logging.INFO)
        
    subprocess.check_call(["gcloud", "auth", "configure-docker", "--quiet"])
    subprocess.check_call(["gcloud", "auth", "activate-service-account", 
                           "--key-file=" + os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
                           "--quiet"])
    
def copy_data_to_nfs(nfs_path, model_dir):
    if not os.path.exists(nfs_path):
        shutil.copytree("ames_dataset", nfs_path)

    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
