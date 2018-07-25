import apache_beam as beam

import code_search.dataflow.cli.arguments as arguments
import code_search.dataflow.transforms.github_bigquery as gh_bq
import code_search.dataflow.transforms.github_batch_predict as github_batch_predict
import code_search.dataflow.do_fns.dict_to_csv as dict_to_csv


def create_batch_predict_pipeline(argv=None):
  """Creates Batch Prediction Pipeline using trained model.

  At a high level, this pipeline does the following things:
    - Read the Processed Github Dataset from BigQuery
    - Encode the functions using T2T problem
    - Get function embeddings using `kubeflow_batch_predict.dataflow.batch_prediction`
    - All results are stored in a BigQuery dataset (`args.target_dataset`)
    - See `transforms.github_dataset.GithubBatchPredict` for details of tables created
    - Additionally, store CSV of docstring, original functions and other metadata for
      reverse index lookup during search engine queries.
  """
  args = arguments.parse_arguments(argv)
  pipeline_opts = arguments.create_pipeline_opts(args)

  pipeline = beam.Pipeline(options=pipeline_opts)

  # TODO(sanyamkapoor): update to new table
  token_pairs = (pipeline
    | "Read Transformed Github Dataset" >> gh_bq.ReadTransformedGithubDataset(
        args.project, dataset=args.target_dataset, table='function_docstrings')
    | "Run Batch Prediction" >> github_batch_predict.GithubBatchPredict(args.project,
                                                                        args.target_dataset,
                                                                        args.problem,
                                                                        args.data_dir,
                                                                        args.saved_model_dir)
  )

  (token_pairs  # pylint: disable=expression-not-assigned
    | "Format for CSV Write" >> beam.ParDo(dict_to_csv.DictToCSVString(
        ['nwo', 'path', 'function_name', 'lineno', 'original_function', 'function_embedding']))
    | "Write CSV" >> beam.io.WriteToText('{}/func-index'.format(args.data_dir),
                                         file_name_suffix='.csv')
  )

  result = pipeline.run()
  if args.runner == 'DirectRunner':
    result.wait_until_finish()


if __name__ == '__main__':
  create_batch_predict_pipeline()
