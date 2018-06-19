import re
from google.cloud import storage


def is_gcs_path(src):
  return bool(re.match(r'gs://([^/]+)(/.+)?', src))

def parse_gcs_path(src):
  if not is_gcs_path(src):
    raise ValueError("{} is not a valid GCS path".format(src))

  _, full_path = src.split('//')
  bucket_name, bucket_path = full_path.split('/', 1)
  return bucket_name, bucket_path


def download_gcs_file(src, target):
  storage_client = storage.Client()
  bucket_name, bucket_path = parse_gcs_path(src)
  bucket = storage_client.get_bucket(bucket_name)
  blob = bucket.blob(bucket_path)
  blob.download_to_filename(target)
