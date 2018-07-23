import json
import requests
import nmslib
import numpy as np
from tensor2tensor import problems  # pylint: disable=unused-import
from code_search.t2t.query import get_encoder_decoder, encode_query


class CodeSearchEngine:
  """This is a utility class which takes an nmslib
  index file and a data file to return data from"""
  def __init__(self, problem: str, data_dir: str, serving_url: str,
               index_file: str):
    self._serving_url = serving_url
    self._problem = problem
    self._data_dir = data_dir
    self._index_file = index_file

    self.index = CodeSearchEngine.nmslib_init()
    self.index.loadIndex(index_file)

  def embed(self, query_str):
    """Get query embedding from TFServing

    This involves encoding the input query
    for the TF Serving service
    """
    encoder, _ = get_encoder_decoder(self._problem, self._data_dir)
    encoded_query = encode_query(encoder, query_str)
    data = {"instances": [{"input": {"b64": encoded_query}}]}

    response = requests.post(url=self._serving_url,
                             headers={'content-type': 'application/json'},
                             data=json.dumps(data))

    result = response.json()
    result['predictions'] = [preds['outputs'] for preds in result['predictions']]
    return result

  def query(self, query_str: str, k=2):
    embedding = self.embed(query_str)
    idxs, dists = self.index.knnQuery(embedding, k=k)

    # TODO(sanyamkapoor): initialize data map and return
    # list of dicts
    # [
    #     {'src': self.data_map[idx], 'dist': dist}
    #     for idx, dist in zip(idxs, dists)
    # ]
    return idxs, dists

  @staticmethod
  def nmslib_init():
    """Initializes an nmslib index object"""
    index = nmslib.init(method='hnsw', space='cosinesimil')
    return index

  @staticmethod
  def create_index(data: np.array, save_path: str):
    """Add numpy data to the index and save to path"""
    index = CodeSearchEngine.nmslib_init()
    index.addDataPointBatch(data)
    index.createIndex({'post': 2}, print_progress=True)
    index.saveIndex(save_path)
