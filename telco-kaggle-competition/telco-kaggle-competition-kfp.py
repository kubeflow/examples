import kfp
from kfp import dsl

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
    name = 'telco churn',
    description = 'pipeline to run telco churn')

def  passing_parameter():
    comp2 = PreProcess()
    comp3 = Train(comp2)
    comp4 = Test(comp3)

if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(passing_parameter, __file__[:-3]+ '.yaml')
