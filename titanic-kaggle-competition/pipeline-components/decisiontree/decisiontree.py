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

def decisiontree(train_pickle, train_label):

    train_df = pd.read_pickle(train_pickle)
    train_labels = pd.read_pickle(train_label)

    decision_tree = DecisionTreeClassifier()
    decision_tree.fit(train_df, train_labels)
    acc_decision_tree = round(decision_tree.score(train_df, train_labels) * 100, 2)

    print('decision_tree_acc', acc_decision_tree)
    with open('decision_tree_acc.txt', 'a') as f:
        f.write(str(acc_decision_tree))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--train_pickle')
    parser.add_argument('--train_label')
    args = parser.parse_args()
    decisiontree(args.train_pickle, args.train_label)