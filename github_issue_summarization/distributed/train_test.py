import os
import tempfile
import train
import unittest

class ArgsFake(object):
  pass

class TrainTest(unittest.TestCase):
  #def test_train_keras(self):
    #"""Test training using Keras and not TF.Estimator"""
    #args = ArgsFake()
    #args.model_dir = tempfile.mkdtemp()
    #this_dir = os.path.dirname(__file__)
    #args.data_dir = tempfile.mkdtemp()
    #args.data_file = os.path.join(this_dir, "test_data",
                                  #"github_issues_sample.csv")
    #trainer = train.Trainer(args)
    #trainer.preprocess()
    #trainer.build_model()

    ## TODO(jlewi): Does this run in a reasonable time.
    #trainer.train_keras(epochs=1)

  def test_train(self):
    args = ArgsFake()
    args.model_dir = tempfile.mkdtemp()
    this_dir = os.path.dirname(__file__)
    args.data_dir = tempfile.mkdtemp()
    args.data_file = os.path.join(this_dir, "test_data",
                                  "github_issues_sample.csv")
    trainer = train.Trainer(args)
    trainer.preprocess()
    trainer.build_model()
    trainer.train_estimator()

if __name__ == "__main__":
  unittest.main()