import argparse
import os
import apache_beam.options.pipeline_options as pipeline_options


def create_pipeline_opts(args):
  """Create standard Pipeline Options for Beam"""

  options = pipeline_options.PipelineOptions()
  options.view_as(pipeline_options.StandardOptions).runner = args.runner

  google_cloud_options = options.view_as(pipeline_options.GoogleCloudOptions)
  google_cloud_options.project = args.project
  if args.runner == 'DataflowRunner':
    google_cloud_options.job_name = args.job_name
    google_cloud_options.temp_location = '{}/temp'.format(args.job_bucket)
    google_cloud_options.staging_location = '{}/staging'.format(args.job_bucket)

    worker_options = options.view_as(pipeline_options.WorkerOptions)
    worker_options.num_workers = args.num_workers
    worker_options.max_num_workers = args.max_num_workers
    worker_options.machine_type = args.machine_type

  # Setup file is needed to install all dependencies
  setup_options = options.view_as(pipeline_options.SetupOptions)
  setup_options.setup_file = os.path.abspath(os.path.join(__file__, '../../../../setup.py'))

  return options

def parse_arguments(argv):
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-r', '--runner', metavar='', type=str, default='DirectRunner',
                      help='Type of runner - DirectRunner or DataflowRunner')
  parser.add_argument('-p', '--project', metavar='', type=str,
                      help='Project ID')
  parser.add_argument('-d', '--target-dataset', metavar='', type=str,
                      help='Name of the BigQuery dataset for output results')
  parser.add_argument('--pre-transformed', action='store_true',
                      help='Use a pre-transformed dataset')
  # parser.add_argument('-o', '--output', metavar='', type=str,
  #                     help='Output string of the format <dataset>:<table>')

  predict_args_parser = parser.add_argument_group('Batch Prediction Arguments')
  predict_args_parser.add_argument('--problem', metavar='', type=str,
                                   help='Name of the T2T problem')
  predict_args_parser.add_argument('--data-dir', metavar='', type=str,
                                   help='Path to directory of the T2T problem data')
  predict_args_parser.add_argument('--saved-model-dir', metavar='', type=str,
                                   help='Path to directory containing Tensorflow SavedModel')

  # Dataflow related arguments
  dataflow_args_parser = parser.add_argument_group('Dataflow Runner Arguments')
  dataflow_args_parser.add_argument('-j', '--job-name', metavar='', type=str,
                                    help='Job name')
  dataflow_args_parser.add_argument('--job-bucket', metavar='', type=str,
                                    help='Path to Google Storage Bucket for Dataflow job')
  dataflow_args_parser.add_argument('--num-workers', metavar='', type=int, default=1,
                                    help='Number of workers')
  dataflow_args_parser.add_argument('--max-num-workers', metavar='', type=int, default=1,
                                    help='Maximum number of workers')
  dataflow_args_parser.add_argument('--machine-type', metavar='', type=str, default='n1-standard-1',
                                    help='Google Cloud Machine Type to use')

  parsed_args = parser.parse_args(argv)
  return parsed_args
