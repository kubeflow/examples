import pandas as pd
import os

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
    api.competition_download_file('bluebook-for-bulldozers','TrainAndValid.zip')
    api.competition_download_file('bluebook-for-bulldozers','Test.csv')

download_kaggle_dataset("bluebook-for-bulldozers","/data")

os.listdir("/data")

base_dir='/data'
train_dir_zip=base_dir+'/TrainAndValid.zip'
test_dir_zip=base_dir+'/Test.csv.zip'

from zipfile import ZipFile
with ZipFile(train_dir_zip,'r') as zipObj:
    zipObj.extractall('/data')
    print("Train Archive unzipped")
with ZipFile(test_dir_zip,'r') as zipObj:
    zipObj.extractall('/data')
    print("Test Archive unzipped")

print(os.listdir("/data"))

# train_df = pd.read_json("/data/TrainAndValid.csv", lines=True)
# # # test_df = pd.read_json("test.json", lines=True)
# train_df.head()


# def import_dataset(path):
#     df = pd.read_csv(path, parse_dates = ['saledate'])
#     return df

# df_test_and_valid = import_dataset("/data/TrainAndValid.csv") 

