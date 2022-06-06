import numpy as np
import pandas as pd
# import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib import style
import argparse
from sklearn import linear_model
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import Perceptron
from sklearn.linear_model import SGDClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

def svm(train_pickle, train_label):

    train_df = pd.read_pickle(train_pickle)
    train_labels = pd.read_pickle(train_label)

    linear_svc = SVC(gamma='auto')
    linear_svc.fit(train_df, train_labels)
    acc_linear_svc = round(linear_svc.score(train_df, train_labels) * 100, 2)

    print('svm_acc', acc_linear_svc)
    with open('svm_acc.txt', 'a') as f:
        f.write(str(acc_linear_svc))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--train_pickle')
    parser.add_argument('--train_label')
    args = parser.parse_args()
    svm(args.train_pickle, args.train_label)
    