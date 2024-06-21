import kfp
from kfp import dsl


def SendMsg(trial, epoch, patience):
    vop = dsl.VolumeOp(name="pvc",
                       resource_name="pvc", size='5Gi', 
                       modes=dsl.VOLUME_MODE_RWO)

    return dsl.ContainerOp(
        name = 'Train', 
        image = 'hubdocker76/demotrain:v8',   # use this prebuilt image or replace image with your own custom image
        command = ['python3', 'train.py'],
        arguments=[
            '--trial', trial,
            '--epoch', epoch,
            '--patience', patience
        ],
        pvolumes={
            '/data': vop.volume
        }
    )

def GetMsg(comp1):
    return dsl.ContainerOp(
        name = 'Evaluate',
        image = 'hubdocker76/demoeval:v3',  # use this prebuilt image or replace image with your own custom image
        pvolumes={
            '/data': comp1.pvolumes['/data']
        },
        command = ['python3', 'eval.py']
    )

@dsl.pipeline(
    name = 'face pipeline',
    description = 'pipeline to detect facial landmarks')
def  passing_parameter(trial, epoch, patience):
    comp1 = SendMsg(trial, epoch, patience).add_pod_label("kaggle-secret", "true")
    comp2 = GetMsg(comp1)

if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(passing_parameter, __file__ + '.yaml')


