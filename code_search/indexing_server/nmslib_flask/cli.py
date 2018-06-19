import sys
import os
import argparse
import logging
logging.basicConfig(level=logging.INFO)

from nmslib_flask.gcs import download_gcs_file, is_gcs_path
from nmslib_flask.search_engine import SearchEngine


def parse_args(args):
  parser = argparse.ArgumentParser(prog='NMSLib Flask Server')

  parser.add_argument('--index-file', type=str, required=True,
                     help='Path to index file created by nmslib')
  parser.add_argument('--data-file', type=str, required=True,
                     help='Path to csv file for human-readable data')
  parser.add_argument('--data-dir', type=str, metavar='', default='/tmp',
                     help='Path to working data directory')

  return parser.parse_args(args)

if __name__ == '__main__':
  args = parse_args(sys.argv[1:])

  if not os.path.isdir(args.data_dir):
    os.makedirs(args.data_dir, exist_ok=True)

  # Download relevant files if needed
  index_file = args.index_file
  if is_gcs_path(index_file):
    target_index_file = os.path.join(args.data_dir, os.path.basename(index_file))
    download_gcs_file(index_file, target_index_file)
    index_file = target_index_file

  data_file = args.data_file
  if is_gcs_path(data_file):
    target_data_file = os.path.join(args.data_dir, os.path.basename(data_file))
    download_gcs_file(data_file, target_data_file)
    data_file = target_data_file

  search_engine = SearchEngine(index_file, data_file)

  # TODO: create a Flask server using the search engine object
