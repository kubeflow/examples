import nmslib
import numpy as np


class SearchEngine:
  def __init__(self, index_file: str):
    self.index = SearchEngine.nmslib_init()
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
    index = nmslib.init(method='hnsw', space='cosinesimil')
    return index

  @staticmethod
  def create_index(data: np.array, save_path: str):
    index = SearchEngine.nmslib_init()
    index.addDataPointBatch(data)
    index.createIndex({'post': 2}, print_progress=True)
    index.saveIndex(save_path)
