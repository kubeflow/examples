import numpy as np
import pandas as pd
import os

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
    print('Downloading data to /data ....')
    api.competition_download_file('titanic','train.csv')
    api.competition_download_file('titanic','test.csv')

download_kaggle_dataset("titanic","/data")

os.listdir("/data")


# train_df = pd.read_json("train.json", lines=True)
# test_df = pd.read_json("test.json", lines=True)
# train_df.head()


print('Downloaded data to /data')

# PREDICTION_LABEL = 'Survived'

# test_df = pd.read_csv("test.csv")
# train_df = pd.read_csv("train.csv")

# print('train_df:', train_df.head())
# print('test_df: ', test_df.head())


