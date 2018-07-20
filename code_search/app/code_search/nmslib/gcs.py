import re
import os
from google.cloud import storage


def is_gcs_path(gcs_path_string):
  """
  Checks if strings are of the format
  "gs://bucket_name" or "gs://bucket_name/file/path"
  """
  return bool(re.match(r'gs://([^/]+)(/.+)?', gcs_path_string))

def parse_gcs_path(gcs_path_string):
  """
  Get the bucket name and file path from a valid GCS path
  string (see `is_gcs_path`)
  """
  if not is_gcs_path(gcs_path_string):
    raise ValueError("{} is not a valid GCS path".format(gcs_path_string))

  _, full_path = gcs_path_string.split('//')
  bucket_name, bucket_path = full_path.split('/', 1)
  return bucket_name, bucket_path


def download_gcs_file(src_file, target_file):
  """
  Download a source file to the target file from GCS
  and return the target file path
  """
  storage_client = storage.Client()
  bucket_name, bucket_path = parse_gcs_path(src_file)
  bucket = storage_client.get_bucket(bucket_name)
  blob = bucket.blob(bucket_path)
  blob.download_to_filename(target_file)
  return target_file


def maybe_download_gcs_file(src_file, target_dir):
  """Wraps `download_gcs_file` with checks"""
  if not is_gcs_path(src_file):
    return src_file

  target_file = os.path.join(target_dir, os.path.basename(src_file))

  return download_gcs_file(src_file, target_file)


def upload_gcs_file(src_file, target_file):
  """
  Upload a source file to the target file in GCS
  and return the target file path
  """
  storage_client = storage.Client()
  bucket_name, bucket_path = parse_gcs_path(target_file)
  bucket = storage_client.get_bucket(bucket_name)
  blob = bucket.blob(bucket_path)
  blob.upload_from_filename(src_file)
  return target_file


def maybe_upload_gcs_file(src_file, target_file):
  """Wraps `upload_gcs_file` with checks"""
  if not is_gcs_path(target_file):
    os.rename(src_file, target_file)
    return target_file

  return upload_gcs_file(src_file, target_file)
