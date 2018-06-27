import sys
import os
import argparse
import numpy as np

from code_search.nmslib.gcs import maybe_download_gcs_file, maybe_upload_gcs_file
from code_search.nmslib.search_engine import CodeSearchEngine
from code_search.nmslib.search_server import CodeSearchServer

def parse_server_args(args):
  parser = argparse.ArgumentParser(prog='nmslib Flask Server')

  parser.add_argument('--tmp-dir', type=str, metavar='', default='/tmp/nmslib',
                     help='Path to temporary data directory')
  parser.add_argument('--index-file', type=str, required=True,
                     help='Path to index file created by nmslib')
  parser.add_argument('--problem', type=str, required=True,
                      help='Name of the T2T problem')
  parser.add_argument('--data-dir', type=str, metavar='', default='/tmp',
                     help='Path to working data directory')
  parser.add_argument('--serving-url', type=str, required=True,
                      help='Complete URL to TF Serving Inference server')
  parser.add_argument('--host', type=str, metavar='', default='0.0.0.0',
                     help='Host to start server on')
  parser.add_argument('--port', type=int, metavar='', default=8008,
                     help='Port to bind server to')

  args = parser.parse_args(args)
  args.tmp_dir = os.path.expanduser(args.tmp_dir)
  args.index_file = os.path.expanduser(args.index_file)
  args.data_dir = os.path.expanduser(args.data_dir)

  return args


def parse_creator_args(args):
  parser = argparse.ArgumentParser(prog='nmslib Index Creator')

  parser.add_argument('--data-file', type=str, required=True,
                     help='Path to csv data file for human-readable data')
  parser.add_argument('--index-file', type=str, metavar='', default='/tmp/index.nmslib',
                     help='Path to output index file')
  parser.add_argument('--tmp-dir', type=str, metavar='', default='/tmp/nmslib',
                     help='Path to temporary data directory')

  return parser.parse_args(args)

def server():
  args = parse_server_args(sys.argv[1:])

  if not os.path.isdir(args.tmp_dir):
    os.makedirs(args.tmp_dir, exist_ok=True)

  # Download relevant files if needed
  index_file = maybe_download_gcs_file(args.index_file, args.tmp_dir)
  # data_file = maybe_download_gcs_file(args.data_file, args.tmp_dir)

  search_engine = CodeSearchEngine(args.problem, args.data_dir, args.serving_url,
                                   index_file)

  search_server = CodeSearchServer(engine=search_engine,
                                   host=args.host, port=args.port)
  search_server.run()


def creator():
  args = parse_creator_args(sys.argv[1:])

  if not os.path.isdir(args.tmp_dir):
    os.makedirs(args.tmp_dir, exist_ok=True)

  data_file = maybe_download_gcs_file(args.data_file, args.tmp_dir)

  # TODO(sanyamkapoor): parse data file into a numpy array

  data = np.load(data_file)

  tmp_index_file = os.path.join(args.tmp_dir, os.path.basename(args.index_file))

  CodeSearchEngine.create_index(data, tmp_index_file)

  maybe_upload_gcs_file(tmp_index_file, args.index_file)
