import kfp
from kfp import dsl

def LoadData():
    vop = dsl.VolumeOp(name="pvc",
                       resource_name="pvc", size='1Gi', 
                       modes=dsl.VOLUME_MODE_RWO)

    return dsl.ContainerOp(
        name = 'load-data', 
        image = 'hubdocker76/titanic-load-data:v2', 
        command = ['python3', 'load.py'],
        pvolumes={
            '/data': vop.volume
        }
    )

def PreProcess(comp1):
    return dsl.ContainerOp(
        name = 'preprocess',
        image = 'hubdocker76/titanic-pre-process-data:v1',
        command = ['python3', 'preprocess.py'],
        pvolumes = {
            '/data': comp1.pvolumes['/data']
        }
    )

def featurengg(comp2):
    return dsl.ContainerOp(
        name = 'featureengineering',
        image = 'hubdocker76/titanic-feature-engg:v6',
        command = ['python3', 'featureengg.py'],
        pvolumes={
            '/data': comp2.pvolumes['/data']
        }
    )

def RandomForest(comp3):
    return dsl.ContainerOp(
        name = 'RandomForest',
        image = 'hubdocker76/titanic-randomforest:v1',
        pvolumes={
            '/data': comp3.pvolumes['/data']
        },
        command = ['python3', 'randomforest.py']
    )

def regression(comp3):
    return dsl.ContainerOp(
        name = 'Logisticregression',
        image = 'hubdocker76/titanic-regression:v1',
        pvolumes={
            '/data': comp3.pvolumes['/data']
        },
        command = ['python3', 'regression.py']
    )

def bayes(comp3):
    return dsl.ContainerOp(
        name = 'naivebayes',
        image = 'hubdocker76/titanic-bayes:v1',
        pvolumes={
            '/data': comp3.pvolumes['/data']
        },
        command = ['python3', 'naivebayes.py']
    )

def svm(comp3):
    return dsl.ContainerOp(
        name = 'svm',
        image = 'hubdocker76/titanic-svm:v1',
        pvolumes={
            '/data': comp3.pvolumes['/data']
        },
        command = ['python3', 'svm.py']
    )

def decisiontree(comp3):
    return dsl.ContainerOp(
        name = 'decisiontree',
        image = 'hubdocker76/titanic-decisiontree:v1',
        pvolumes={
            '/data': comp3.pvolumes['/data']
        },
        command = ['python3', 'decisiontree.py']
    )

# def result(comp4, comp5, comp6, comp7, comp8):
#     return dsl.ContainerOp(
#         name = 'result',
#         image = 'hubdocker76/titanic-results:v1',
#         # comp4, comp5, comp6, comp7, comp8
#         pvolumes={
#             '/data': comp8.pvolumes['/data']
#         },
#         # arguments=[
#         #     '--comp4',comp4,
#         #     '--comp5',comp5,
#         #     '--comp6',comp6,
#         #     '--comp7',comp7,
#         #     '--comp8',comp8
#         # ],
        
        
#         command = ['python3', 'result.py']

#     )

@dsl.pipeline(
    name = 'Titanic',
    description = 'pipeline to run Kaggle titanic challenge')

def  passing_parameter():
    comp1 = LoadData().add_pod_label("kaggle-secret", "true")
    comp2 = PreProcess(comp1)
    comp3 = featurengg(comp2)
    comp4 = RandomForest(comp3)
    comp5 = regression(comp3)
    comp6 = bayes(comp3)
    comp7 = svm(comp3)
    comp8 = decisiontree(comp3)
    # comp9 = result(comp4, comp5, comp6, comp7, comp8)

if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(passing_parameter, __file__[:-3] + '.yaml')
