"""
This module serves as the entrypoint to either create an nmslib index or
start a Flask server to serve the index via a simple REST interface. It
internally talks to TF Serving for inference related tasks. The
two entrypoints `server` and `creator` are exposed as `nmslib-create`
and `nmslib-serve` binaries (see `setup.py`). Use `-h` to get a list
of input CLI arguments to both.
"""

import os
import argparse

from code_search.nmslib.gcs import maybe_download_gcs_file, maybe_upload_gcs_file
from code_search.nmslib.search_engine import CodeSearchEngine
from code_search.nmslib.search_server import CodeSearchServer

def parse_server_args(args):
  parser = argparse.ArgumentParser(prog='nmslib Flask Server')

  parser.add_argument('--tmp-dir', type=str, metavar='', default='/tmp/nmslib',
                     help='Path to temporary data directory')
  parser.add_argument('--data-file', type=str, required=True,
                     help='Path to CSV file containing human-readable data')
  parser.add_argument('--index-file', type=str, required=True,
                     help='Path to index file created by nmslib')
  parser.add_argument('--problem', type=str, required=True,
                      help='Name of the T2T problem')
  parser.add_argument('--data-dir', type=str, required=True,
                     help='Path to working data directory')
  parser.add_argument('--serving-url', type=str, required=True,
                      help='Complete URL to TF Serving Inference server')
  parser.add_argument('--host', type=str, metavar='', default='0.0.0.0',
                     help='Host to start server on')
  parser.add_argument('--port', type=int, metavar='', default=8008,
                     help='Port to bind server to')

  args = parser.parse_args(args)
  args.tmp_dir = os.path.expanduser(args.tmp_dir)
  args.data_file = os.path.expanduser(args.data_file)
  args.index_file = os.path.expanduser(args.index_file)
  args.data_dir = os.path.expanduser(args.data_dir)

  return args

def server(argv=None):
  args = parse_server_args(argv)

  if not os.path.isdir(args.tmp_dir):
    os.makedirs(args.tmp_dir, exist_ok=True)

  # Download relevant files if needed
  index_file = maybe_download_gcs_file(args.index_file, args.tmp_dir)
  data_file = maybe_download_gcs_file(args.data_file, args.tmp_dir)

  search_engine = CodeSearchEngine(args.problem, args.data_dir, args.serving_url,
                                   index_file, data_file)

  search_server = CodeSearchServer(engine=search_engine,
                                   host=args.host, port=args.port)
  search_server.run()
