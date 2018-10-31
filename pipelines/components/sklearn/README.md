### Overview
This ML component is for model training using scikit-learn.

### Intended Use
You may use this component to train a scikit-learn classifier or regressor. Currently, the following estimators are supported:

* AdaBoostClassifier
* BaggingClassifier
* DecisionTreeClassifier
* ExtraTreesClassifier
* GaussianNB
* GaussianProcessClassifier
* GradientBoostingClassifier
* GradientBoostingRegressor
* KDTree
* KNeighborsClassifier
* KNeighborsRegressor
* Lasso
* LinearRegression
* LogisticRegression
* MLPClassifier
* RandomForestClassifier
* Ridge
* SGDRegressor
* SVC
* SVR

### Input
* estimator_name: The name of the estimator as it appears in the list above.
* training_data_path: path to the training csv file. The code expects the csv file to have no headers; and the target to be the first column, followed by the features.
* test_data_path: path to the test csv file, with a format similar to the training data file.
* output_dir: path to the output directory.
* You may also pass the hyperparameters just like another argument

#### Example:
```
python src/task.py 
    --training_data_path ./iris_train.csv 
    --test_data_path ./iris_test.csv
    --output_dir ./output_directory
    --estimator_name GradientBoostingClassifier 
    --n_estimators 100 
    --max_depth 4 
```

### Output
The code produces two timestamped files upon succession:
* `%ESTIMATOR_NAME%_%TIMESTAMP%.pkl`: The trained model
* `%ESTIMATOR_NAME%_%TIMESTAMP%_report.yaml`: The job training report file

