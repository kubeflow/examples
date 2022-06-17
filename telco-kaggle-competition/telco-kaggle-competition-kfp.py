import kfp
from kfp import dsl

# def LoadData():
#     vop = dsl.VolumeOp(name="pvc",
#                        resource_name="pvc", size='1Gi', 
#                        modes=dsl.VOLUME_MODE_RWO)

#     return dsl.ContainerOp(
#         name = 'load-data', 
#         image = 'hubdocker76/bulldozers:v6', 
#         command = ['python3', 'load.py'],

#         pvolumes={
#             '/data': vop.volume
#         }
#     )

def PreProcess():
    vop = dsl.VolumeOp(name="pvc",
                    resource_name="pvc", size='1Gi', 
                    modes=dsl.VOLUME_MODE_RWO)

    return dsl.ContainerOp(
        name = 'preprocess',
        image = 'hubdocker76/telco-preprocess:v2',
        pvolumes={
            '/data': vop.volume
        },
        command = ['python3', 'preprocess.py']
    )

def Train(comp2):
    return dsl.ContainerOp(
        name = 'train',
        image = 'hubdocker76/telco-train:v9',
        pvolumes={
            '/data': comp2.pvolumes['/data']
        },
        command = ['python3', 'train.py']
    )

def Test(comp3):
    return dsl.ContainerOp(
        name = 'test',
        image = 'hubdocker76/telco-test:v2',
        pvolumes={
            '/data': comp3.pvolumes['/data']
        },
        command = ['python3', 'test.py']
    )


@dsl.pipeline(
    name = 'blue book for bulldozers',
    description = 'pipeline to run blue book for bulldozers')

def  passing_parameter():
    # comp1 = LoadData().add_pod_label("kaggle-secret", "true")
    comp2 = PreProcess()
    comp3 = Train(comp2)
    comp4 = Test(comp3)

if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(passing_parameter, __file__[:-3]+ '.yaml')
