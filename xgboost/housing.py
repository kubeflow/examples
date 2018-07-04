import argparse
import numpy as np
import pandas as pd
from sklearn.preprocessing import Imputer
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error

def read_input(file_name):
    data = pd.read_csv(file_name[0])
    data.dropna(axis=0, subset=['SalePrice'], inplace=True)

    y = data.SalePrice
    X = data.drop(['SalePrice'], axis=1).select_dtypes(exclude=['object'])

    train_X, test_X, train_y, test_y = train_test_split(X.values, y.values, test_size=0.25)
    
    imputer = Imputer()
    train_X = imputer.fit_transform(train_X)
    test_X = imputer.transform(test_X)

    return (train_X, train_y), (test_X, test_y)

def train_model(train_X,
                train_y,
                test_X,
                test_y,
                n_estimators,
                learning_rate):
    model = XGBRegressor(n_estimators=n_estimators,
                         learning_rate=learning_rate)

    model.fit(train_X,
              train_y,
              early_stopping_rounds=5,
              eval_set=[(test_X, test_y)], verbose=False)
    return model

def eval_model(model, test_X, test_y):
    predictions = model.predict(test_X)
    print("Mean Absolute Error : " + str(mean_absolute_error(predictions, test_y)))


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '--train-input',
            help="Input training file",
            nargs='+',
            required=True
    )
    parser.add_argument(
            '--n-estimators',
            help='Number of trees in the model',
            type=int,
            default=1000
    )
    parser.add_argument(
            '--learning-rate',
            help='Learning rate for the model',
            default=0.1
    )

    args = parser.parse_args()
    
    (train_X, train_y), (test_X, test_y) = read_input(args.train_input)
    model = train_model(train_X,
                        train_y,
                        test_X,
                        test_y,
                        args.n_estimators,
                        args.learning_rate)

    eval_model(model, test_X, test_y)
