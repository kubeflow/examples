import numpy as np
import os
# from sklearn.utils import shuffle           
# import matplotlib.pyplot as plt             
import tensorflow as tf                
import pandas as pd
from tensorflow.keras.models import load_model
import os
# import shutil
import argparse
import autokeras as ak

### Declaring input arguments 

parser = argparse.ArgumentParser()
parser.add_argument('--trial', type=int)
parser.add_argument('--epoch', type=int)
parser.add_argument('--patience', type=int)

args = vars(parser.parse_args())

trials = args['trial']
epochs = args['epoch']
patience = args['patience']

project="Facial-keypoints"
run_id= "1.8"
resume_run = True

MAX_TRIALS=trials
EPOCHS=epochs
PATIENCE=patience

### Data Extraction : extract data and save to attached extenal pvc at location /data ###

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
    api.competition_download_file('facial-keypoints-detection','training.zip')
    api.competition_download_file('facial-keypoints-detection','test.zip')



download_kaggle_dataset("facial-keypoints-detection","/data")



base_dir='/data'
train_dir_zip=base_dir+'/training.zip'
test_dir_zip=base_dir+'/test.zip'

from zipfile import ZipFile
with ZipFile(train_dir_zip,'r') as zipObj:
    zipObj.extractall('/data')
    print("Train Archive unzipped")
with ZipFile(test_dir_zip,'r') as zipObj:
    zipObj.extractall('/data')
    print("Test Archive unzipped")


## Data preprocess 

train_dir='/data/training.csv'
test_dir='/data/test.csv'
train=pd.read_csv(train_dir)
test=pd.read_csv(test_dir)

train=train.dropna()
train=train.reset_index(drop=True)

X_train=[]
Y_train=[]

for img in train['Image']:
    X_train.append(np.asarray(img.split(),dtype=float).reshape(96,96,1))
X_train=np.reshape(X_train,(-1,96,96,1))
X_train = np.asarray(X_train).astype('float32')
    
for i in range(len((train))): 
    Y_train.append(np.asarray(train.iloc[i][0:30].to_numpy()))
Y_train = np.asarray(Y_train).astype('float32')


## Data training

reg = ak.ImageRegressor(max_trials=MAX_TRIALS)
reg.fit(X_train, Y_train, validation_split=0.15, epochs=EPOCHS)

# Export trained model to externally attached pvc 
my_model = reg.export_model()
my_model.save('/data/model_autokeras', save_format="tf")
