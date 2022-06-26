import json
import numpy as np
import pandas as pd
# import tensorflow as tf
import argparse
import os

# from tensorflow.keras.preprocessing.text import Tokenizer

# parser = argparse.ArgumentParser()
# parser.add_argument('--LR')
# parser.add_argument('--EPOCHS')
# parser.add_argument('--BATCH_SIZE')
# parser.add_argument('--EMBED_DIM', type=int)
# parser.add_argument('--HIDDEN_DIM' type=int)
# parser.add_argument('--DROPOUT', type=float)
# parser.add_argument('--SP_DROPOUT', type=float)
# parser.add_argument('--TRAIN_SEQUENCE_LENGTH', type=int)

# args = vars(parser.parse_args())

# lr = args['LR']
# epochs = args['EPOCHS']
# batchsize = args['BATCH_SIZE']
# embeddim = args['EMBED_DIM']
# hiddendim = args['HIDDEN_DIM']
# dropout = args['DROPOUT']
# spdropout = args['SP_DROPOUT']
# trainsequencelength = args['TRAIN_SEQUENCE_LENGTH']

# LR=lr
# EPOCHS=epochs
# BATCH_SIZE=batchsize
# EMBED_DIM=embeddim
# HIDDEN_DIM=hiddendim
# DROPOUT=dropout
# SP_DROPOUT=spdropout
# TRAIN_SEQUENCE_LENGTH=trainsequencelength

### Data Download and load data: download data using Kaggle API and save it to attached extenal pvc at location /data ###

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
    api.competition_download_file('stanford-covid-vaccine','train.json')
    api.competition_download_file('stanford-covid-vaccine','test.json')

download_kaggle_dataset("stanford-covid-vaccine","/data")

os.listdir("/data")

base_dir='/data'
train_dir_zip=base_dir+'/train.json.zip'
test_dir_zip=base_dir+'/test.json.zip'

from zipfile import ZipFile
with ZipFile(train_dir_zip,'r') as zipObj:
    zipObj.extractall('/data')
    print("Train Archive unzipped")
with ZipFile(test_dir_zip,'r') as zipObj:
    zipObj.extractall('/data')
    print("Test Archive unzipped")

os.listdir("/data")

train_df = pd.read_json("train.json", lines=True)
test_df = pd.read_json("test.json", lines=True)
train_df.head()


