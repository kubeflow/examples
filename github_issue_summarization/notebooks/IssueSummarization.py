from __future__ import print_function

import dill as dpickle
import numpy as np
from keras.models import load_model

from seq2seq_utils import Seq2Seq_Inference


class IssueSummarization(object):

    def __init__(self):
        with open('body_pp.dpkl', 'rb') as f:
            body_pp = dpickle.load(f)
        with open('title_pp.dpkl', 'rb') as f:
            title_pp = dpickle.load(f)
        self.model = Seq2Seq_Inference(encoder_preprocessor=body_pp,
                                       decoder_preprocessor=title_pp,
                                       seq2seq_model=load_model('seq2seq_model_tutorial.h5'))

    def predict(self, X, feature_names):
        return np.asarray([[self.model.generate_issue_title(body[0])[1]] for body in X])
