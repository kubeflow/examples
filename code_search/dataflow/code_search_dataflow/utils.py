import ast
import astor
import base64
from nltk.tokenize import RegexpTokenizer
import spacy
from tensor2tensor.utils import registry
from tensor2tensor.data_generators import text_encoder
import tensorflow as tf


def tokenize_docstring(text):
  """Apply tokenization using spacy to docstrings."""
  en = spacy.load('en')
  tokens = en.tokenizer(text.decode('utf8', 'ignore'))
  return [token.text.lower() for token in tokens if not token.is_space]


def tokenize_code(text):
  """A very basic procedure for tokenizing code strings."""
  return RegexpTokenizer(r'\w+').tokenize(text)


def get_function_docstring_pairs(blob):
  """Extract (function/method, docstring) pairs from a given code blob."""
  pairs = []
  try:
    module = ast.parse(blob)
    classes = [node for node in module.body if isinstance(node, ast.ClassDef)]
    functions = [node for node in module.body if isinstance(node, ast.FunctionDef)]
    for _class in classes:
      functions.extend([node for node in _class.body if isinstance(node, ast.FunctionDef)])

    for f in functions:
      source = astor.to_source(f)
      docstring = ast.get_docstring(f) if ast.get_docstring(f) else ''
      func = source.replace(ast.get_docstring(f, clean=False), '') if docstring else source

      pairs.append((f.name, f.lineno, source, ' '.join(tokenize_code(func)),
                    ' '.join(tokenize_docstring(docstring.split('\n\n')[0]))))
  except (AssertionError, MemoryError, SyntaxError, UnicodeEncodeError):
    pass
  return pairs


def get_encoder(problem_name, data_dir):
  """Get encoder from the T2T problem.

  This might vary by problem, keeping generic
  as a reference.
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
