import numpy as np
import pandas as pd
# import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib import style

from sklearn import linear_model
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import Perceptron
from sklearn.linear_model import SGDClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

train_df = pd.read_pickle('/data/train')
train_labels = pd.read_pickle('/data/label')

decision_tree = DecisionTreeClassifier()
decision_tree.fit(train_df, train_labels)
acc_decision_tree = round(decision_tree.score(train_df, train_labels) * 100, 2)


myfile = open("/data/decisiontree.txt","a")#append mode
print("writing file ..", acc_decision_tree)
myfile.write(str(acc_decision_tree))
myfile.close()
