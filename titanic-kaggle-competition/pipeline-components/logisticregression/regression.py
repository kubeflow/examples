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


def regression(train_pickle, train_label):
        
    train_df = pd.read_pickle(train_pickle)
    train_labels = pd.read_pickle(train_label)

    logreg = LogisticRegression(solver='lbfgs', max_iter=110)
    logreg.fit(train_df, train_labels)
    acc_log = round(logreg.score(train_df, train_labels) * 100, 2)
    print('acc_log', acc_log)

    with open('regression_acc.txt', 'a') as f:
        f.write(str(acc_log))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--train_pickle')
    parser.add_argument('--train_label')
    args = parser.parse_args()
    regression(args.train_pickle, args.train_label)