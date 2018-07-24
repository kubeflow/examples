"""Entrypoint for Dataflow jobs"""

from __future__ import print_function
import argparse
import os
import apache_beam as beam
import apache_beam.options.pipeline_options as pipeline_options

import code_search.dataflow.transforms.process_github_files as process_github_files
import code_search.dataflow.transforms.code_embed as code_embed


def create_pipeline_opts(args):
  """Create standard Pipeline Options for Beam"""

  options = pipeline_options.PipelineOptions()
  options.view_as(pipeline_options.StandardOptions).runner = args.runner

  google_cloud_options = options.view_as(pipeline_options.GoogleCloudOptions)
  google_cloud_options.project = args.project
  if args.runner == 'DataflowRunner':
    google_cloud_options.job_name = args.job_name
    google_cloud_options.temp_location = '{}/temp'.format(args.storage_bucket)
    google_cloud_options.staging_location = '{}/staging'.format(args.storage_bucket)

    worker_options = options.view_as(pipeline_options.WorkerOptions)
    worker_options.num_workers = args.num_workers
    worker_options.max_num_workers = args.max_num_workers
    worker_options.machine_type = args.machine_type

  setup_options = options.view_as(pipeline_options.SetupOptions)
  setup_options.setup_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'setup.py')

  return options

def parse_arguments(argv):
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-r', '--runner', metavar='', type=str, default='DirectRunner',
                      help='Type of runner - DirectRunner or DataflowRunner')
  parser.add_argument('-o', '--output', metavar='', type=str,
                      help='Output string of the format <dataset>:<table>')

  predict_args_parser = parser.add_argument_group('Batch Prediction Arguments')
  predict_args_parser.add_argument('--problem', metavar='', type=str,
                                   help='Name of the T2T problem')
  predict_args_parser.add_argument('--data-dir', metavar='', type=str,
                                   help='aPath to directory of the T2T problem data')
  predict_args_parser.add_argument('--saved-model-dir', metavar='', type=str,
                                   help='Path to directory containing Tensorflow SavedModel')

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
  pipeline_opts = create_pipeline_opts(args)

  pipeline = beam.Pipeline(options=pipeline_opts)
  (pipeline #pylint: disable=expression-not-assigned
    | process_github_files.ProcessGithubFiles(args.project,
                                    args.output, args.storage_bucket)
  )
  result = pipeline.run()
  if args.runner == 'DirectRunner':
    result.wait_until_finish()


def create_batch_predict_pipeline(argv=None):
  """Creates Batch Prediction Pipeline using trained model.

  This pipeline takes in a collection of CSV files returned
  by the Github Pipeline, embeds the code text using the
  trained model in a given model directory.
  """
  args = parse_arguments(argv)
  pipeline_opts = create_pipeline_opts(args)

  pipeline = beam.Pipeline(options=pipeline_opts)
  (pipeline  #pylint: disable=expression-not-assigned
    | code_embed.GithubBatchPredict(args.project, args.problem,
                                    args.data_dir, args.saved_model_dir)
  )
  result = pipeline.run()
  if args.runner == 'DirectRunner':
    result.wait_until_finish()
