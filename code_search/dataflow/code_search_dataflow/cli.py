"""Entrypoint for Dataflow jobs"""

from __future__ import print_function
import argparse
import os
import apache_beam as beam
from apache_beam.options.pipeline_options import GoogleCloudOptions
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from apache_beam.options.pipeline_options import StandardOptions
from apache_beam.options.pipeline_options import WorkerOptions

from code_search_dataflow.transforms import ProcessGithubFiles


def create_pipeline_opts(args):
  """Create standard Pipeline Options for Beam"""

  options = PipelineOptions()
  options.view_as(StandardOptions).runner = args.runner

  if args.runner == 'DataflowRunner':
    google_cloud_options = options.view_as(GoogleCloudOptions)
    google_cloud_options.project = args.project
    google_cloud_options.job_name = args.job_name
    google_cloud_options.temp_location = '{}/temp'.format(args.storage_bucket)
    google_cloud_options.staging_location = '{}/staging'.format(args.storage_bucket)

    options.view_as(WorkerOptions).num_workers = args.num_workers
    options.view_as(WorkerOptions).max_num_workers = args.max_num_workers
    options.view_as(WorkerOptions).machine_type = args.machine_type

    # Point to `setup.py` to allow Dataflow runner to install the package
    options.view_as(SetupOptions).setup_file = os.path.join(
      os.path.dirname(os.path.dirname(__file__)), 'setup.py')

  return options

def parse_arguments(argv):
  default_script_file = os.path.abspath('{}/../../files/select_github_archive.sql'.format(__file__))

  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-r', '--runner', metavar='', type=str, default='DirectRunner')
  parser.add_argument('-i', '--input', metavar='', type=str, default=default_script_file,
                      help='Path to BigQuery SQL script')
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

  parsed_args = parser.parse_args(argv)
  return parsed_args


def main(argv=None):
  args = parse_arguments(argv)
  pipeline_opts = create_pipeline_opts(args)

  with open(args.input, 'r') as f:
    query_string = f.read()

  pipeline = beam.Pipeline(options=pipeline_opts)
  (pipeline | ProcessGithubFiles(args.project, query_string, args.output, args.storage_bucket)) #pylint: disable=expression-not-assigned
  pipeline.run()


if __name__ == '__main__':
  import sys
  main(sys.argv[1:])
