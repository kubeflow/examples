from __future__ import print_function
import argparse
import apache_beam as beam

from preprocess.pipeline import create_pipeline_opts, ProcessGithubFiles


def parse_arguments(args):
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('-i', '--input', metavar='', type=str, help='Path to BigQuery SQL script')
  parser.add_argument('-o', '--output', metavar='', type=str,
                      help='Output string of the format <dataset>:<table>')
  parser.add_argument('-p', '--project', metavar='', type=str, default='Project', help='Project ID')
  parser.add_argument('-j', '--job-name', metavar='', type=str, default='Beam Job', help='Job name')
  parser.add_argument('--storage-bucket', metavar='', type=str, default='gs://bucket',
                      help='Path to Google Storage Bucket')
  parser.add_argument('--num-workers', metavar='', type=int, default=1, help='Number of workers')
  parser.add_argument('--max-num-workers', metavar='', type=int, default=1,
                      help='Maximum number of workers')
  parser.add_argument('--machine-type', metavar='', type=str, default='n1-standard-1',
                      help='Google Cloud Machine Type to use')

  parsed_args = parser.parse_args(args)
  return parsed_args


def main(args):
  args = parse_arguments(args)
  pipeline_opts = create_pipeline_opts(args)

  with open(args.input, 'r') as f:
    query_string = f.read()

  pipeline = beam.Pipeline(options=pipeline_opts)
  (pipeline | ProcessGithubFiles(args.project, query_string, args.output)) #pylint: disable=expression-not-assigned
  pipeline.run()


if __name__ == '__main__':
  import sys
  main(sys.argv[1:])
