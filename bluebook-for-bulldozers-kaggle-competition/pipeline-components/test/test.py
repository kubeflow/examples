import pandas as pd
import os
import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
from sklearn.metrics import mean_squared_log_error, mean_absolute_error

import joblib
from sklearn.ensemble import RandomForestClassifier

def import_dataset(path):
    df = pd.read_csv(path, parse_dates = ['saledate'])
    return df
    
# import test data
df_test=import_dataset('/data/Test.csv')
df_test.head()

def enrich_df(df):
    """
    Adds following columns to dataframe saleYear, saleMonth, saleDay, saledayOfWeek, saleDayOfYear
    """
    temp_dict={
    "saleYear":"year",
    "saleMonth":"month",
    "saleDay":"day",
    "saleDayOfWeek":"dayofweek",
    "saleDayOfYear":"dayofyear"
    }
    
    for column, attribute in temp_dict.items():
        df[column] = df["saledate"].dt.__getattribute__(attribute)
    return df

def preprocess_dataframe_for_model(df):
    # change all srting type to categorical type
    for label, content in df.items():
        if pd.api.types.is_string_dtype(content):
            df[label]=df[label].astype("category").cat.as_ordered()
            
    # enrich the dataframe 
    enrich_df(df)
    df.drop("saledate",axis=1,inplace=True)
    
    # fill the numerical missing values with median and non-numerical values with their (category no. + 1)      
    for label, content in df.items():
        if pd.api.types.is_numeric_dtype(content):
            if pd.isnull(content).sum():
                df[label]=content.fillna(content.median())
        else:
            df[label]=pd.Categorical(content).codes+1
    return df



df_test_modified=preprocess_dataframe_for_model(df_test)

ideal_model = joblib.load("data/ideal_model.joblib")

test_preds=ideal_model.predict(df_test_modified)

df_preds=pd.DataFrame()

df_preds["SalesID"]=df_test_modified.SalesID
df_preds["SalePrice"]=test_preds
print(df_preds)
df_preds.to_csv("/data/SalePrice-Submission.csv",index=False)

