import ast
import astor
import nltk.tokenize as tokenize
import spacy


def tokenize_docstring(text):
  """Tokenize docstrings.

  Args:
    text: A docstring to be tokenized.

  Returns:
    A list of strings representing the tokens in the docstring.
  """
  en = spacy.load('en')
  tokens = en.tokenizer(text.decode('utf8'))
  return [token.text.lower() for token in tokens if not token.is_space]


def tokenize_code(text):
  """Tokenize code strings.

  This simply considers whitespaces as token delimiters.

  Args:
    text: A code string to be tokenized.

  Returns:
    A list of strings representing the tokens in the code.
  """
  return tokenize.RegexpTokenizer(r'\w+').tokenize(text)


def get_function_docstring_pairs(blob):
  """Extract (function/method, docstring) pairs from a given code blob.

  This method reads a string representing a Python file, builds an
  abstract syntax tree (AST) and returns a list of Docstring and Function
  pairs along with supporting metadata.

  Args:
    blob: A string representing the Python file contents.

  Returns:
    A list of tuples of the form:
      [
        (
          function_name,
          lineno,
          original_function,
          function_tokens,
          docstring_tokens
        ),
        ...
      ]
  """
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
      pair_tuple = (
        f.name.decode('utf-8'),
        str(f.lineno).decode('utf-8'),
        source.decode('utf-8'),
        ' '.join(tokenize_code(func)).decode('utf-8'),
        ' '.join(tokenize_docstring(docstring.split('\n\n')[0])).decode('utf-8'),
      )
      pairs.append(pair_tuple)
  except (AssertionError, MemoryError, SyntaxError, UnicodeEncodeError):
    pass
  return pairs
