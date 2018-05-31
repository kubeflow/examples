import ast
import astor
import spacy
from nltk.tokenize import RegexpTokenizer


def tokenize_docstring(text):
    """Apply tokenization using spacy to docstrings."""
    en = spacy.load('en')
    tokens = en.tokenizer(text.decode('utf8'))
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
