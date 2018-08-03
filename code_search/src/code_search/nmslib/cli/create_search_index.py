import argparse
import csv
import numpy as np
import os
import tensorflow as tf

import code_search.nmslib.search_engine as search_engine


def parse_creator_args(args):
  parser = argparse.ArgumentParser(prog='Code Search Index Creator')

  parser.add_argument('--data_dir', type=str, metavar='',
                     help='Path to directory with CSV files containing function embeddings')
  parser.add_argument('--lookup_file', type=str, metavar='',
                     help='Path to output CSV file for reverse index lookup.')
  parser.add_argument('--index_file', type=str, metavar='',
                     help='Path to output index file')
  parser.add_argument('--tmp_dir', type=str, metavar='', default='/tmp/code_search',
                     help='Path to temporary data directory')

  args = parser.parse_args(args)
  args.data_dir = os.path.expanduser(args.data_dir)
  args.lookup_file = os.path.expanduser(args.lookup_file)
  args.index_file = os.path.expanduser(args.index_file)
  args.tmp_dir = os.path.expanduser(args.tmp_dir)

  return args


def create_search_index(argv=None):
  """Create NMSLib index and a reverse lookup CSV file.

  This routine reads a list CSV data files at a given
  directory, combines them into one for reverse lookup
  and uses the embeddings string to create an NMSLib index.
  This embedding is the last column of all CSV files.

  Args:
    argv: A list of strings representing command line arguments.
  """
  tf.logging.set_verbosity(tf.logging.INFO)

  args = parse_creator_args(argv)

  if not os.path.isdir(args.tmp_dir):
    os.makedirs(args.tmp_dir)

  tmp_index_file = os.path.join(args.tmp_dir, os.path.basename(args.index_file))
  tmp_lookup_file = os.path.join(args.tmp_dir, os.path.basename(args.lookup_file))

  embeddings_data = []

  with open(tmp_lookup_file, 'w') as lookup_file:
    lookup_writer = csv.writer(lookup_file)

    for csv_file_path in tf.gfile.Glob('{}/*.csv'.format(args.data_dir)):
      tf.logging.debug('Reading {}'.format(csv_file_path))

      with tf.gfile.Open(csv_file_path) as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
          embedding_string = row[-1]
          embedding_vector = [float(value) for value in embedding_string.split(',')]
          embeddings_data.append(embedding_vector)

          lookup_writer.writerow(row[:-1])

  embeddings_data = np.array(embeddings_data)

  search_engine.CodeSearchEngine.create_index(embeddings_data, tmp_index_file)

  tf.gfile.Copy(tmp_lookup_file, args.lookup_file)
  tf.gfile.Copy(tmp_index_file, args.index_file)


if __name__ == '__main__':
  create_search_index()
