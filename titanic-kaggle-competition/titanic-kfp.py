import kfp
from kfp import dsl

def preprocess_op():

    return dsl.ContainerOp(
        name='Preprocess Data',
        image='hubdocker76/titanic-pre-process-data:v9',
        arguments=[],
        file_outputs={
            'train_pickle': '/app/train',
            'test_pickle': '/app/test',
        }
    )

def featureengineering_op(train_pickle, test_pickle):

    return dsl.ContainerOp(
        name='featureengineering',
        image='hubdocker76/titanic-feature-engineering:v8',
        arguments=[
            '--train_pickle', train_pickle,
            '--test_pickle', test_pickle
        ],
        file_outputs={
            'train_pickle_out': '/app/train_v2',
            'train_label_out': '/app/train_label_v2',
        }
    )

def regression_op(train_pickle_out, train_label_out):

    return dsl.ContainerOp(
        name='regression',
        image='hubdocker76/titanic-logistic-regression:v5',
        arguments=[
            '--train_pickle', train_pickle_out,
            '--train_label', train_label_out,
        ],
        file_outputs={
            'regression_acc': '/app/regression_acc.txt'
        }
    )

def bayes_op(train_pickle_out, train_label_out):

    return dsl.ContainerOp(
        name='bayes',
        image='hubdocker76/titanic-bayes:v6',
        arguments=[
            '--train_pickle', train_pickle_out,
            '--train_label', train_label_out,
        ],
        file_outputs={
            'bayes_acc': '/app/bayes_acc.txt'
        }
    )

def random_forest_op(train_pickle_out, train_label_out):

    return dsl.ContainerOp(
        name='random_forest',
        image='hubdocker76/titanic-randomforest:v4',
        arguments=[
            '--train_pickle', train_pickle_out,
            '--train_label', train_label_out,
        ],
        file_outputs={
            'random_forest_acc': '/app/random_forest_acc.txt'
        }
    )

def decision_tree_op(train_pickle_out, train_label_out):

    return dsl.ContainerOp(
        name='decision_tree',
        image='hubdocker76/titanic-decision-tree:v1',
        arguments=[
            '--train_pickle', train_pickle_out,
            '--train_label', train_label_out,
        ],
        file_outputs={
            'decision_tree_acc': '/app/decision_tree_acc.txt'
        }
    )

def svm_op(train_pickle_out, train_label_out):

    return dsl.ContainerOp(
        name='svm',
        image='hubdocker76/titanic-svm:v2',
        arguments=[
            '--train_pickle', train_pickle_out,
            '--train_label', train_label_out,
        ],
        file_outputs={
            'svm_acc': '/app/svm_acc.txt'
        }
    )

def result_model_op(bayes_acc, regression_acc, random_forest_acc, decision_tree_acc, svm_acc):

    return dsl.ContainerOp(
        name='results',
        image='hubdocker76/titanic-results:v9',
        arguments=[
            '--bayes_acc', bayes_acc,
            '--regression_acc', regression_acc,
            '--random_forest_acc', random_forest_acc,
            '--decision_tree_acc', decision_tree_acc,
            '--svm_acc', svm_acc
        ]
    )

@dsl.pipeline(
   name='Titanic',
   description='Kubeflow pipeline of kaggle Titanic competition '
)
def boston_pipeline():
    _preprocess_op = preprocess_op().add_pod_label("kaggle-secret", "true")
    
    _featureengineering_op = featureengineering_op(
        dsl.InputArgumentPath(_preprocess_op.outputs['train_pickle']),
        dsl.InputArgumentPath(_preprocess_op.outputs['test_pickle'])
    ).after(_preprocess_op)

    _regression_op = regression_op(
        dsl.InputArgumentPath(_featureengineering_op.outputs['train_pickle_out']),
        dsl.InputArgumentPath(_featureengineering_op.outputs['train_label_out'])
    ).after(_featureengineering_op)

    _bayes_op = bayes_op(
        dsl.InputArgumentPath(_featureengineering_op.outputs['train_pickle_out']),
        dsl.InputArgumentPath(_featureengineering_op.outputs['train_label_out'])
    ).after(_featureengineering_op)

    _random_forest_op = random_forest_op(
        dsl.InputArgumentPath(_featureengineering_op.outputs['train_pickle_out']),
        dsl.InputArgumentPath(_featureengineering_op.outputs['train_label_out'])
    ).after(_featureengineering_op)

    _decision_tree_op = decision_tree_op(
        dsl.InputArgumentPath(_featureengineering_op.outputs['train_pickle_out']),
        dsl.InputArgumentPath(_featureengineering_op.outputs['train_label_out'])
    ).after(_featureengineering_op)

    _svm_op = svm_op(
        dsl.InputArgumentPath(_featureengineering_op.outputs['train_pickle_out']),
        dsl.InputArgumentPath(_featureengineering_op.outputs['train_label_out'])
    ).after(_featureengineering_op)

    # result_model_op(
    #     dsl.InputArgumentPath(_featureengineering_op.outputs['model'])
    # ).after(_test_op, _test_op2)

    result_model_op(
        dsl.InputArgumentPath(_bayes_op.outputs['bayes_acc']),
        dsl.InputArgumentPath(_regression_op.outputs['regression_acc']),
        dsl.InputArgumentPath(_random_forest_op.outputs['random_forest_acc']),
        dsl.InputArgumentPath(_decision_tree_op.outputs['decision_tree_acc']),
        dsl.InputArgumentPath(_svm_op.outputs['svm_acc'])
    ).after(_regression_op, _bayes_op, _random_forest_op, _decision_tree_op, _svm_op)

# client = kfp.Client()
# client.create_run_from_pipeline_func(boston_pipeline, arguments={})

if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(boston_pipeline, __file__[:-3] + '.yaml')