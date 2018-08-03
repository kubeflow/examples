import csv
import json
import os
import functools
import requests
import tensorflow as tf

import code_search.nmslib.cli.arguments as arguments
import code_search.t2t.query as query
from code_search.nmslib.search_engine import CodeSearchEngine
from code_search.nmslib.search_server import CodeSearchServer


def embed_query(encoder, serving_url, query_str):
  data = {"instances": [{"input": {"b64": encoder(query_str)}}]}

  response = requests.post(url=serving_url,
                           headers={'content-type': 'application/json'},
                           data=json.dumps(data))

  result = response.json()
  return result['predictions'][0]['outputs']


def start_search_server(argv=None):
  """Start a Flask REST server.

  This routine starts a Flask server which maintains
  an in memory index and a reverse-lookup database of
  Python files which can be queried via a simple REST
  API. It also serves the UI for a friendlier interface.

  Args:
    argv: A list of strings representing command line arguments.
  """
  tf.logging.set_verbosity(tf.logging.INFO)

  args = arguments.parse_arguments(argv)

  if not os.path.isdir(args.tmp_dir):
    os.makedirs(args.tmp_dir)

  tf.logging.debug('Reading {}'.format(args.lookup_file))
  lookup_data = []
  with tf.gfile.Open(args.lookup_file) as lookup_file:
    reader = csv.reader(lookup_file)
    for row in reader:
      lookup_data.append(row)

  tmp_index_file = os.path.join(args.tmp_dir, os.path.basename(args.index_file))

  tf.logging.debug('Reading {}'.format(args.index_file))
  if not os.path.isfile(tmp_index_file):
    tf.gfile.Copy(args.index_file, tmp_index_file)

  encoder = query.get_encoder(args.problem, args.data_dir)
  query_encoder = functools.partial(query.encode_query, encoder)
  embedding_fn = functools.partial(embed_query, query_encoder, args.serving_url)

  search_engine = CodeSearchEngine(tmp_index_file, lookup_data, embedding_fn)
  search_server = CodeSearchServer(search_engine, args.ui_dir, host=args.host, port=args.port)
  search_server.run()


if __name__ == '__main__':
  start_search_server()
