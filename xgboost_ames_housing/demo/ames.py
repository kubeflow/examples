from google.cloud import storage
from kubernetes import client as k8s_client
from kubernetes import config as k8s_config
import logging
import os
import re
import joblib
import sys
from pathlib import Path
import pprint
import pandas as pd
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
import time
from xgboost import XGBRegressor
import yaml

def read_input(file_name, test_size=0.25):
    """Read input data and split it into train and test."""
    
    if file_name.startswith("gs://"):
        gcs_path = file_name
        train_bucket_name, train_path = split_gcs_uri(gcs_path)

        storage_client = storage.Client()
        train_bucket = storage_client.get_bucket(train_bucket_name)   
        train_blob = train_bucket.blob(train_path)

        file_name = "/tmp/data.csv"
        train_blob.download_to_filename(file_name)
    
    data = pd.read_csv(file_name)
    data.dropna(axis=0, subset=['SalePrice'], inplace=True)

    y = data.SalePrice
    X = data.drop(['SalePrice'], axis=1).select_dtypes(exclude=['object'])

    train_X, test_X, train_y, test_y = train_test_split(X.values,
                                                      y.values,
                                                      test_size=test_size,
                                                      shuffle=False)

    imputer = SimpleImputer()
    train_X = imputer.fit_transform(train_X)
    test_X = imputer.transform(test_X)

    return (train_X, train_y), (test_X, test_y)

def load_model(model_path):
    local_model_path = model_path
    
    if model_path.startswith("gs://"):        
        gcs_path = model_path
        train_bucket_name, train_path = split_gcs_uri(gcs_path)

        storage_client = storage.Client()
        train_bucket = storage_client.get_bucket(train_bucket_name)   
        train_blob = train_bucket.blob(train_path)

        local_model_path = "/tmp/model.dat"
        logging.info("Downloading model to %s", local_model_path) 
        train_blob.download_to_filename(local_model_path)
        
    model = joblib.load(local_model_path)
    return model
   
def train_model(train_X,
                train_y,
                test_X,
                test_y,
                n_estimators,
                learning_rate):
    """Train the model using XGBRegressor."""
    model = XGBRegressor(n_estimators=n_estimators, learning_rate=learning_rate)

    model.fit(train_X,
            train_y,
            early_stopping_rounds=40,
            eval_set=[(test_X, test_y)])

    logging.info("Best RMSE on eval: %.2f with %d rounds",
                 model.best_score,
                 model.best_iteration+1)
    return model

def eval_model(model, test_X, test_y):
    """Evaluate the model performance."""
    predictions = model.predict(test_X)
    logging.info("mean_absolute_error=%.2f", mean_absolute_error(predictions, test_y))

def save_model(model, model_file):
    """Save XGBoost model for serving."""
    
    gcs_path = None
    if model_file.startswith("gs://"):
        gcs_path = model_file        
        model_file = "/tmp/model.dat"        
    joblib.dump(model, model_file)
    logging.info("Model export success: %s", model_file)
    
    if gcs_path:
        model_bucket_name, model_path = split_gcs_uri(gcs_path)
        storage_client = storage.Client()
        model_bucket = storage_client.get_bucket(model_bucket_name)   
        model_blob = model_bucket.blob(model_path)
    
        logging.info("Uploading model to %s", gcs_path)
        model_blob.upload_from_filename(model_file)
        
    
def split_gcs_uri(gcs_uri):
    """Split a GCS URI into bucket and path."""
    GCS_REGEX = re.compile("gs://([^/]*)(/.*)?")
    m = GCS_REGEX.match(gcs_uri)
    bucket = m.group(1)
    path = ""
    if m.group(2):
        path = m.group(2).lstrip("/")
    return bucket, path

def create_pr_to_update_model(job_spec_file, model_file):
    """Submit a K8s job to generate the model.
    
    Args:
      job_spec_file: Path to yaml file for the K8s job to update the model
      model_file: Value to use for the model file.
    """
    k8s_config.incluster_config.load_incluster_config()
    kclient = k8s_client.ApiClient()
    logging.info("K8s master: %s", kclient.configuration.host)
                 
    with open(job_spec_file) as hf:
        job_spec = yaml.load(hf)
    
    command = job_spec["spec"]["template"]["spec"]["containers"][0]["command"]
    for i, v in enumerate(command):
        if not "--model-file" in v:
            continue

        command[i] = "--model-file=" + model_file
        break

    logging.info("Creating job to update model to %s", model_file)
    batch_client = k8s_client.BatchV1Api(kclient)
    job_resp = batch_client.create_namespaced_job(job_spec["metadata"]["namespace"], job_spec)
    namespace = job_spec["metadata"]["namespace"]
    name = job_resp.metadata.name
    logging.info("Created job %s.%s", namespace,name)    
    while True:
        latest_job = batch_client.read_namespaced_job(name, namespace)

        last_condition = None
        if latest_job.status.conditions:
            last_condition = latest_job.status.conditions[-1]

        logging.info("Waiting for job %s.%s; Last condition %s", namespace, name,
                     pprint.pformat(last_condition))

        if last_condition:
            if last_condition.type.lower() == "complete":
                logging.info("Job %s.%s is done", namespace, name)
                break

        time.sleep(10)

    logging.info("Final job:\n%s", pprint.pformat(latest_job))
    
def deploy_model(model_file):
    # TODO(jlewi): Write actual code to deploy model; we could use fairing
    logging.info("Deploying model %s", model_file)
    
def validate_model(endpoint):
    # TODO(jlewi): Write actual code to validate the model
    logging.info("Validating model at %s", endpoint)
    
    