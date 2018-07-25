import apache_beam as beam

import code_search.dataflow.cli.arguments as arguments
import code_search.dataflow.transforms.github_bigquery as gh_bq
import code_search.dataflow.transforms.github_dataset as github_dataset
import code_search.dataflow.do_fns.dict_to_csv as dict_to_csv


def create_github_pipeline(argv=None):
  """Creates the Github pre-processing pipeline.

  At a high level, this pipeline does the following things:
    - Read Github Python files from BigQuery
    - If Github Python files have already been process, use the
      pre-processed table instead (using flag `--pre-transformed`)
    - Tokenize files into pairs of function definitions and docstrings
    - All results are stored in a BigQuery dataset (`args.target_dataset`)
    - See `transforms.github_dataset.TransformGithubDataset` for details of tables created
    - Additionally, store pairs of docstring and function tokens in a CSV file
      for training
  """
  args = arguments.parse_arguments(argv)
  pipeline_opts = arguments.create_pipeline_opts(args)

  pipeline = beam.Pipeline(options=pipeline_opts)

  if args.pre_transformed:
    token_pairs = (pipeline
      | "Read Transformed Github Dataset" >> gh_bq.ReadTransformedGithubDataset(
        args.project, dataset=args.target_dataset, table='function_docstrings')
    )
  else:
    token_pairs = (pipeline
      | "Read Github Dataset" >> gh_bq.ReadGithubDataset(args.project)
      | "Transform Github Dataset" >> github_dataset.TransformGithubDataset(args.project,
                                                                            args.target_dataset)
    )

  (token_pairs  # pylint: disable=expression-not-assigned
    | "Format for CSV Write" >> beam.ParDo(dict_to_csv.DictToCSVString(
      ['docstring_tokens', 'function_tokens']))
    | "Write CSV" >> beam.io.WriteToText('{}/func-doc-pairs'.format(args.data_dir),
                                         file_name_suffix='.csv')
  )

  result = pipeline.run()
  if args.runner == 'DirectRunner':
    result.wait_until_finish()


if __name__ == '__main__':
  create_github_pipeline()
