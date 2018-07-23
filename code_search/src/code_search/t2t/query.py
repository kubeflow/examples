import base64
import tensorflow as tf
from tensor2tensor.data_generators import text_encoder
from tensor2tensor.utils import registry


def get_encoder(problem_name, data_dir):
  """Get encoder from the T2T problem.This might
  vary by problem, keeping generic as a reference
  """
  problem = registry.problem(problem_name)
  hparams = tf.contrib.training.HParams(data_dir=data_dir)
  problem.get_hparams(hparams)
  return problem.feature_info["inputs"].encoder


def encode_query(encoder, query_str):
  """Encode the input query string using encoder. This
  might vary by problem but keeping generic as a reference.
  Note that in T2T problems, the 'targets' key is needed
  even though it is ignored during inference.
  See tensorflow/tensor2tensor#868"""

  encoded_str = encoder.encode(query_str) + [text_encoder.EOS_ID]
  features = {"inputs": tf.train.Feature(int64_list=tf.train.Int64List(value=encoded_str)),
              "targets": tf.train.Feature(int64_list=tf.train.Int64List(value=[0]))}
  example = tf.train.Example(features=tf.train.Features(feature=features))
  return base64.b64encode(example.SerializeToString()).decode('utf-8')

def decode_result(decoder, list_ids):
  return decoder.decode(list_ids)
