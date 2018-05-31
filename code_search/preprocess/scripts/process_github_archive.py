from __future__ import print_function
import argparse
import apache_beam as beam

from preprocess.pipeline import create_pipeline_opts, BigQueryGithubFiles


def parse_arguments(args):
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('-i', '--input', metavar='', help='Path to BigQuery SQL script')
  parser.add_argument('-o', '--output', metavar='',
                      help='Output string of the format <dataset>:<table>')
  parser.add_argument('-p', '--project', metavar='', default='Project', help='Project ID')
  parser.add_argument('-j', '--job-name', metavar='', default='Beam Job', help='Job name')
  parser.add_argument('--storage-bucket', metavar='', default='gs://bucket',
                      help='Path to Google Storage Bucket')

  parsed_args = parser.parse_args(args)
  return parsed_args


def main(args):
  args = parse_arguments(args)
  pipeline_opts = create_pipeline_opts(args)

  with open(args.input, 'r') as f:
    query_string = f.read()

  pipeline = beam.Pipeline(options=pipeline_opts)
  (pipeline | BigQueryGithubFiles(args.project, query_string, args.output)) #pylint: disable=expression-not-assigned
  pipeline.run()


if __name__ == '__main__':
  import sys
  main(sys.argv[1:])
