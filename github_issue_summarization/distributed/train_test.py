import os
import tempfile
import train
import unittest

class ArgsFake(object):
  pass

class TrainTest(unittest.TestCase):
  def test_train(self):
    args = ArgsFake()
    args.model_dir = tempfile.mkdtemp()
    this_dir = os.path.dirname(__file__)
    args.data_dir = tempfile.mkdtemp()
    args.data_file = os.path.join(this_dir, "test_data",
                                  "github_issues_sample.csv")
    train.train_model(args)

if __name__ == "__main__":
  unittest.main()