import pandas as pd
import os
import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
from sklearn.metrics import mean_squared_log_error, mean_absolute_error

import joblib
from sklearn.ensemble import RandomForestClassifier

# Create evaluation function (the competition uses Root Mean Square Log Error)

def rmsle(y_test, y_preds):
    return np.sqrt(mean_squared_log_error(y_test, y_preds))

# Create function to evaluate our model
def show_scores(model):
    train_preds = model.predict(X_train)
    val_preds = model.predict(X_valid)
    scores = {"Training MAE": mean_absolute_error(y_train, train_preds),
              "Valid MAE": mean_absolute_error(y_valid, val_preds),
              "Training RMSLE": rmsle(y_train, train_preds),
              "Valid RMSLE": rmsle(y_valid, val_preds),
              "Training R^2": model.score(X_train, y_train),
              "Valid R^2": model.score(X_valid, y_valid)}
    return scores


model = RandomForestRegressor(n_jobs=-1,random_state=42)


df_test_and_valid_modified = pd.read_pickle("/data/df_test_and_valid_modified.pkl") 



df_train=df_test_and_valid_modified[df_test_and_valid_modified.saleYear!=2012]
df_valid=df_test_and_valid_modified[df_test_and_valid_modified.saleYear==2012]

X_train, y_train= df_train.drop(["SalePrice"],axis=1), df_train.SalePrice
X_valid, y_valid= df_valid.drop(["SalePrice"],axis=1), df_valid.SalePrice

search_grid={
    "n_estimators": np.arange(10, 30, 5),
    "max_depth": [None, 3, 5, 10],
    "min_samples_split": np.arange(2, 10, 4),
    "min_samples_leaf": np.arange(1, 10, 4),
    "max_features": [0.5, 1, "sqrt", "auto"],
    "max_samples": [10000]
}

lis=search_grid.values()
pro=1
for index,li in enumerate(lis):
    pro=len(li)*pro
print(f'Now we will fit {pro*2} models')

ideal_model=GridSearchCV(
    RandomForestRegressor(),
    param_grid=search_grid,
    n_jobs=-1,
    cv=2
)

ideal_model.fit(X_train,y_train)
joblib.dump(ideal_model, "/data/ideal_model.joblib")

print(ideal_model.best_params_)


print(show_scores(ideal_model))

