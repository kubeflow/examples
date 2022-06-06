import numpy as np
import pandas as pd
import os
import sys

def preprocess_data():
    def download_kaggle_dataset(data_set:str, path:str):
        import os
        import glob
        with open('/secret/kaggle/KAGGLE_KEY', 'r') as file:
            kaggle_key = file.read().rstrip()
        with open('/secret/kaggle/KAGGLE_USERNAME', 'r') as file:
            kaggle_user = file.read().rstrip()
            
        os.environ['KAGGLE_USERNAME'] = kaggle_user 
        os.environ['KAGGLE_KEY'] = kaggle_key

        import kaggle
        from kaggle.api.kaggle_api_extended import KaggleApi
        os.chdir(os.environ.get('HOME'))
        os.system("mkdir " + path)
        os.chdir(path)
        print('\n Authenticating Kaggle Api ....')
        api = KaggleApi()
        api.authenticate()
        print('Downloading data to /app ....')
        api.competition_download_file('titanic','train.csv')
        api.competition_download_file('titanic','test.csv')

    download_kaggle_dataset("titanic","/app")

    os.listdir('/app')


    # train_df = pd.read_json("train.json", lines=True)
    # test_df = pd.read_json("test.json", lines=True)
    # train_df.head()


    print('Downloaded data to /app')


    test_df = pd.read_csv("test.csv")
    train_df = pd.read_csv("train.csv")



    data = [train_df, test_df]
    # print(data)

    for dataset in data:
        dataset['relatives'] = dataset['SibSp'] + dataset['Parch']
        dataset.loc[dataset['relatives'] > 0, 'not_alone'] = 0
        dataset.loc[dataset['relatives'] == 0, 'not_alone'] = 1
        dataset['not_alone'] = dataset['not_alone'].astype(int)
    train_df['not_alone'].value_counts()

    # This does not contribute to a person survival probability
    train_df = train_df.drop(['PassengerId'], axis=1)

    import re
    deck = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "U": 8}
    data = [train_df, test_df]

    for dataset in data:
        dataset['Cabin'] = dataset['Cabin'].fillna("U0")
        dataset['Deck'] = dataset['Cabin'].map(lambda x: re.compile("([a-zA-Z]+)").search(x).group())
        dataset['Deck'] = dataset['Deck'].map(deck)
        dataset['Deck'] = dataset['Deck'].fillna(0)
        dataset['Deck'] = dataset['Deck'].astype(int)
    # we can now drop the cabin feature
    train_df = train_df.drop(['Cabin'], axis=1)
    test_df = test_df.drop(['Cabin'], axis=1)

    data = [train_df, test_df]

    for dataset in data:
        mean = train_df["Age"].mean()
        std = test_df["Age"].std()
        is_null = dataset["Age"].isnull().sum()
        # compute random numbers between the mean, std and is_null
        rand_age = np.random.randint(mean - std, mean + std, size = is_null)
        # fill NaN values in Age column with random values generated
        age_slice = dataset["Age"].copy()
        age_slice[np.isnan(age_slice)] = rand_age
        dataset["Age"] = age_slice
        dataset["Age"] = train_df["Age"].astype(int)
    train_df["Age"].isnull().sum()

    train_df['Embarked'].describe()

    # fill with most common value
    common_value = 'S'
    data = [train_df, test_df]

    for dataset in data:
        dataset['Embarked'] = dataset['Embarked'].fillna(common_value)



    # train_df.to_pickle('/data/train')
    # test_df.to_pickle('/data/test')
    print(train_df.head())
    train_df.to_pickle('train')
    train_df.to_pickle('test')

    # preprocess_out = 'preprocess_compelete'
    # myfile = open("/data/preprocess.txt","a")#append mode
    # print("writing file ..", preprocess_out)
    # myfile.write(str(preprocess_out))
    # myfile.close()

if __name__ == '__main__':
     print('Preprocessing data...')
     preprocess_data()