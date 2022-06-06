import numpy as np
import pandas as pd
import argparse

def result(bayes_acc, regression_acc, random_forest_acc, decision_tree_acc, svm_acc):

    with open(random_forest_acc) as fp:
        for line in fp:
            acc_random_forest=float(line)
    print("reading file ..", acc_random_forest)


    with open(decision_tree_acc) as fp:
        for line in fp:
            acc_decision_tree=float(line)
    print("reading file ..", acc_decision_tree)

    with open(regression_acc) as fp:
        for line in fp:
            acc_regression=float(line)
    print("reading file ..", acc_regression)

    with open(bayes_acc) as fp:
        for line in fp:
            acc_bayes=float(line)
    print("reading file ..", acc_bayes)


    with open(svm_acc) as fp:
        for line in fp:
            acc_svm=float(line)
    print("reading file ..", acc_svm)


    results = pd.DataFrame({
        'Model': ['randomforest', 'decisiontree', 'logisticregression', 'naivebayes', 'svm'],
        'Score': [acc_random_forest, acc_decision_tree, acc_regression, acc_bayes, acc_svm]})
    result_df = results.sort_values(by='Score', ascending=False)
    result_df = result_df.set_index('Score')
    print(result_df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bayes_acc')
    parser.add_argument('--regression_acc')
    parser.add_argument('--random_forest_acc')
    parser.add_argument('--decision_tree_acc')
    parser.add_argument('--svm_acc')
    args = parser.parse_args()
    result(args.bayes_acc, args.regression_acc, args.random_forest_acc, args.decision_tree_acc, args.svm_acc)