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
import os


def featureengineering(train_pickle, test_pickle):

    train_df = pd.read_pickle(train_pickle)
    test_df = pd.read_pickle(test_pickle)

    data = [train_df, test_df]

    for dataset in data:
        dataset['Fare'] = dataset['Fare'].fillna(0)
        dataset['Fare'] = dataset['Fare'].astype(int)

    data = [train_df, test_df]
    titles = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Rare": 5}

    for dataset in data:
        # extract titles
        dataset['Title'] = dataset.Name.str.extract(' ([A-Za-z]+)\.', expand=False)
        # replace titles with a more common title or as Rare
        dataset['Title'] = dataset['Title'].replace(['Lady', 'Countess','Capt', 'Col','Don', 'Dr',\
                                                'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')
        dataset['Title'] = dataset['Title'].replace('Mlle', 'Miss')
        dataset['Title'] = dataset['Title'].replace('Ms', 'Miss')
        dataset['Title'] = dataset['Title'].replace('Mme', 'Mrs')
        # convert titles into numbers
        dataset['Title'] = dataset['Title'].map(titles)
        # filling NaN with 0, to get safe
        dataset['Title'] = dataset['Title'].fillna(0)
    train_df = train_df.drop(['Name'], axis=1)
    test_df = test_df.drop(['Name'], axis=1)

    genders = {"male": 0, "female": 1}
    data = [train_df, test_df]

    for dataset in data:
        dataset['Sex'] = dataset['Sex'].map(genders)

    train_df = train_df.drop(['Ticket'], axis=1)
    test_df = test_df.drop(['Ticket'], axis=1)

    ports = {"S": 0, "C": 1, "Q": 2}
    data = [train_df, test_df]

    for dataset in data:
        dataset['Embarked'] = dataset['Embarked'].map(ports)

    data = [train_df, test_df]
    for dataset in data:
        dataset['Age'] = dataset['Age'].astype(int)
        dataset.loc[ dataset['Age'] <= 11, 'Age'] = 0
        dataset.loc[(dataset['Age'] > 11) & (dataset['Age'] <= 18), 'Age'] = 1
        dataset.loc[(dataset['Age'] > 18) & (dataset['Age'] <= 22), 'Age'] = 2
        dataset.loc[(dataset['Age'] > 22) & (dataset['Age'] <= 27), 'Age'] = 3
        dataset.loc[(dataset['Age'] > 27) & (dataset['Age'] <= 33), 'Age'] = 4
        dataset.loc[(dataset['Age'] > 33) & (dataset['Age'] <= 40), 'Age'] = 5
        dataset.loc[(dataset['Age'] > 40) & (dataset['Age'] <= 66), 'Age'] = 6
        dataset.loc[ dataset['Age'] > 66, 'Age'] = 6

    # let's see how it's distributed train_df['Age'].value_counts()

    data = [train_df, test_df]

    for dataset in data:
        dataset.loc[ dataset['Fare'] <= 7.91, 'Fare'] = 0
        dataset.loc[(dataset['Fare'] > 7.91) & (dataset['Fare'] <= 14.454), 'Fare'] = 1
        dataset.loc[(dataset['Fare'] > 14.454) & (dataset['Fare'] <= 31), 'Fare']   = 2
        dataset.loc[(dataset['Fare'] > 31) & (dataset['Fare'] <= 99), 'Fare']   = 3
        dataset.loc[(dataset['Fare'] > 99) & (dataset['Fare'] <= 250), 'Fare']   = 4
        dataset.loc[ dataset['Fare'] > 250, 'Fare'] = 5
        dataset['Fare'] = dataset['Fare'].astype(int)

    data = [train_df, test_df]
    for dataset in data:
        dataset['Age_Class']= dataset['Age']* dataset['Pclass']

    for dataset in data:
        dataset['Fare_Per_Person'] = dataset['Fare']/(dataset['relatives']+1)
        dataset['Fare_Per_Person'] = dataset['Fare_Per_Person'].astype(int)
    # Let's take a last look at the training set, before we start training the models.
    # train_df.head(10)

    PREDICTION_LABEL = 'Survived'

    train_labels = train_df[PREDICTION_LABEL]
    train_df = train_df.drop(PREDICTION_LABEL, axis=1)

    print('train_labels, train_df')

    # export to pickle
    # train_df.to_pickle('train')
    # train_labels.to_pickle('label')
    print(train_labels.head())
    train_df.to_pickle('train_v2')
    train_labels.to_pickle('train_label_v2')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--train_pickle')
    parser.add_argument('--test_pickle')
    args = parser.parse_args()
    featureengineering(args.train_pickle, args.test_pickle)