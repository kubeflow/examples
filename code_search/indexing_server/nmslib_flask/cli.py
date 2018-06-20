import sys
import os
import argparse
import numpy as np
from nmslib_flask.gcs import maybe_download_gcs_file, maybe_upload_gcs_file
from nmslib_flask.search_engine import CodeSearchEngine
from nmslib_flask.search_server import CodeSearchServer

def parse_server_args(args):
  parser = argparse.ArgumentParser(prog='nmslib Flask Server')

  parser.add_argument('--index-file', type=str, required=True,
                     help='Path to index file created by nmslib')
  parser.add_argument('--data-file', type=str, required=True,
                     help='Path to csv file for human-readable data')
  parser.add_argument('--data-dir', type=str, metavar='', default='/tmp',
                     help='Path to working data directory')
  parser.add_argument('--host', type=str, metavar='', default='0.0.0.0',
                     help='Host to start server on')
  parser.add_argument('--port', type=int, metavar='', default=8008,
                     help='Port to bind server to')

  return parser.parse_args(args)


def parse_creator_args(args):
  parser = argparse.ArgumentParser(prog='nmslib Index Creator')

  parser.add_argument('--data-file', type=str, required=True,
                     help='Path to csv data file for human-readable data')
  parser.add_argument('--output-file', type=str, metavar='', default='/tmp/index.nmslib',
                     help='Path to output index file')
  parser.add_argument('--data-dir', type=str, metavar='', default='/tmp',
                     help='Path to working data directory')

  return parser.parse_args(args)

def server():
  args = parse_server_args(sys.argv[1:])

  if not os.path.isdir(args.data_dir):
    os.makedirs(args.data_dir, exist_ok=True)

  # Download relevant files if needed
  index_file = maybe_download_gcs_file(args.index_file, args.data_dir)
  data_file = maybe_download_gcs_file(args.data_file, args.data_dir)

  search_engine = CodeSearchEngine(index_file, data_file)

  search_server = CodeSearchServer(engine=search_engine,
                                   host=args.host, port=args.port)
  search_server.run()


def creator():
  args = parse_creator_args(sys.argv[1:])

  if not os.path.isdir(args.data_dir):
    os.makedirs(args.data_dir, exist_ok=True)

  data_file = maybe_download_gcs_file(args.data_file, args.data_dir)

  # TODO(sanyamkapoor): parse data file into a numpy array

  data = np.load(data_file)

  tmp_output_file = os.path.join(args.data_dir, os.path.basename(args.output_file))

  CodeSearchEngine.create_index(data, tmp_output_file)

  maybe_upload_gcs_file(tmp_output_file, args.output_file)
