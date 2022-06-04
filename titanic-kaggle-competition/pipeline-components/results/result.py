import numpy as np
import pandas as pd

with open('/data/randomforest.txt') as fp:
    for line in fp:
        acc_random_forest=float(line)
print("reading file ..", acc_random_forest)


with open('/data/decisiontree.txt') as fp:
    for line in fp:
        acc_decision_tree=float(line)
print("reading file ..", acc_decision_tree)

with open('/data/bayes.txt') as fp:
    for line in fp:
        acc_gaussian=float(line)
print("reading file ..", acc_gaussian)

with open('/data/svm.txt') as fp:
    for line in fp:
        acc_linear_svc=float(line)
print("reading file ..", acc_linear_svc)


with open('/data/regression.txt') as fp:
    for line in fp:
        acc_log=float(line)
print("reading file ..", acc_log)


results = pd.DataFrame({
    'Model': ['Support Vector Machines', 'logistic Regression',
              'Random Forest', 'Naive Bayes', 'Decision Tree'],
    'Score': [acc_linear_svc, acc_log,
              acc_random_forest, acc_gaussian, acc_decision_tree]})
result_df = results.sort_values(by='Score', ascending=False)
result_df = result_df.set_index('Score')
print(result_df)