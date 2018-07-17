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
from code_search_dataflow.transforms import GithubCodeEmbed


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
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-r', '--runner', metavar='', type=str, default='DirectRunner',
                      help='Type of runner - DirectRunner or DataflowRunner')
  parser.add_argument('-i', '--input', metavar='', type=str, default='',
                      help='Path to input file')
  parser.add_argument('-o', '--output', metavar='', type=str,
                      help='Output string of the format <dataset>:<table>')

  # Dataflow related arguments
  dataflow_args_parser = parser.add_argument_group('Dataflow Runner Arguments')
  dataflow_args_parser.add_argument('-p', '--project', metavar='', type=str, default='Project',
                                    help='Project ID')
  dataflow_args_parser.add_argument('-j', '--job-name', metavar='', type=str, default='Beam Job',
                                    help='Job name')
  dataflow_args_parser.add_argument('--storage-bucket', metavar='', type=str, default='gs://bucket',
                                    help='Path to Google Storage Bucket')
  dataflow_args_parser.add_argument('--num-workers', metavar='', type=int, default=1,
                                    help='Number of workers')
  dataflow_args_parser.add_argument('--max-num-workers', metavar='', type=int, default=1,
                                    help='Maximum number of workers')
  dataflow_args_parser.add_argument('--machine-type', metavar='', type=str, default='n1-standard-1',
                                    help='Google Cloud Machine Type to use')

  parsed_args = parser.parse_args(argv)
  return parsed_args


def create_github_pipeline(argv=None):
  """Creates the Github source code pre-processing pipeline.

  This pipeline takes an SQL file for BigQuery as an input
  and puts the results in a file and a new BigQuery table.
  An SQL file is included with the module.
  """
  args = parse_arguments(argv)

  default_sql_file = os.path.abspath('{}/../../files/select_github_archive.sql'.format(__file__))
  args.input = args.input or default_sql_file

  pipeline_opts = create_pipeline_opts(args)

  with open(args.input, 'r') as f:
    query_string = f.read()

  pipeline = beam.Pipeline(options=pipeline_opts)
  (pipeline | ProcessGithubFiles(args.project, query_string, args.output, args.storage_bucket)) #pylint: disable=expression-not-assigned
  pipeline.run()


def create_batch_predict_pipeline(argv=None):
  """Creates Batch Prediction Pipeline using trained model.

  This pipeline takes in a collection of CSV files returned
  by the Github Pipeline, embeds the code text using the
  trained model in a given model directory.
  """
  args = parse_arguments(argv)
  pipeline_opts = create_pipeline_opts(args)

  pipeline = beam.Pipeline(options=pipeline_opts)
  (pipeline | GithubCodeEmbed()) #pylint: disable=expression-not-assigned
  pipeline.run()
