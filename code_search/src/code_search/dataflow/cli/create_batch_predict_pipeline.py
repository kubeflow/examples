import apache_beam as beam

import code_search.dataflow.cli.arguments as arguments
import code_search.dataflow.transforms.code_embed as code_embed


def create_batch_predict_pipeline(argv=None):
  """Creates Batch Prediction Pipeline using trained model.

  This pipeline takes in a collection of CSV files returned
  by the Github Pipeline, embeds the code text using the
  trained model in a given model directory.
  """
  args = arguments.parse_arguments(argv)
  pipeline_opts = arguments.create_pipeline_opts(args)

  pipeline = beam.Pipeline(options=pipeline_opts)
  (pipeline  #pylint: disable=expression-not-assigned
    | code_embed.GithubBatchPredict(args.project, args.problem,
                                    args.data_dir, args.saved_model_dir)
  )
  result = pipeline.run()
  if args.runner == 'DirectRunner':
    result.wait_until_finish()


if __name__ == '__main__':
  create_batch_predict_pipeline()
