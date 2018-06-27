import nmslib
import numpy as np


class CodeSearchEngine:
  """This is a utility class which takes an nmslib
  index file and a data file to return data from"""
  def __init__(self, data_dir: str, index_file: str, data_file: str):
    self._data_dir = data_dir
    self._index_file = index_file
    self._data_file = data_file

    self.index = CodeSearchEngine.nmslib_init()
    self.index.loadIndex(index_file)

    # TODO: load the reverse-index map for actual code data
    # self.data_map =

  def embed(self, query_str):
    # TODO load trained model and embed input strings
    raise NotImplementedError

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
