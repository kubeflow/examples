import os
import shutil
import subprocess

KFP_PACKAGE = 'https://storage.googleapis.com/ml-pipeline/release/0.1.20/kfp.tar.gz'
def notebook_setup():
    # Install the SDK

    subprocess.check_call(["pip3", "install", KFP_PACKAGE, "--upgrade"])

    import logging
    import os

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
