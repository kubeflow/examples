import kfp
from kfp import dsl

def SendMsg():
    vop = dsl.VolumeOp(name="pvc",
                       resource_name="pvc", size='1Gi', 
                       modes=dsl.VOLUME_MODE_RWO)

    return dsl.ContainerOp(
        name = 'load-data', 
        image = 'hubdocker76/openvaccine:v10', 
        command = ['python3', 'load.py'],

        pvolumes={
            '/data': vop.volume
        }
    )

def GetMsg(comp1):
    return dsl.ContainerOp(
        name = 'preprocess',
        image = 'hubdocker76/preprocess-data:v10',
        pvolumes={
            '/data': comp1.pvolumes['/data']
        },
        command = ['python3', 'preprocess.py']
    )

def Train(comp2, trial, epoch, batchsize, embeddim, hiddendim, dropout, spdropout, trainsequencelength):
    return dsl.ContainerOp(
        name = 'train',
        image = 'hubdocker76/model-training:v21',
        command = ['python3', 'model.py'],
        arguments=[
            '--LR', trial,
            '--EPOCHS', epoch,
            '--BATCH_SIZE', batchsize,
            '--EMBED_DIM', embeddim,
            '--HIDDEN_DIM', hiddendim,
            '--DROPOUT', dropout,
            '--SP_DROPOUT', spdropout,
            '--TRAIN_SEQUENCE_LENGTH', trainsequencelength
        ],
        pvolumes={
            '/data': comp2.pvolumes['/data']
        }
    )

def Eval(comp1, trial, epoch, batchsize, embeddim, hiddendim, dropout, spdropout, trainsequencelength):
    return dsl.ContainerOp(
        name = 'Evaluate',
        image = 'hubdocker76/eval:v4',
        arguments=[
            '--LR', trial,
            '--EPOCHS', epoch,
            '--BATCH_SIZE', batchsize,
            '--EMBED_DIM', embeddim,
            '--HIDDEN_DIM', hiddendim,
            '--DROPOUT', dropout,
            '--SP_DROPOUT', spdropout,
            '--TRAIN_SEQUENCE_LENGTH', trainsequencelength
        ],
        pvolumes={
            '/data': comp1.pvolumes['/data']
        },
        command = ['python3', 'eval.py']
    )

@dsl.pipeline(
    name = 'openvaccine',
    description = 'pipeline to run openvaccine')

def  passing_parameter(trial, epoch, batchsize, embeddim, hiddendim, dropout, spdropout, trainsequencelength):
    comp1 = SendMsg().add_pod_label("kaggle-secret", "true")
    comp2 = GetMsg(comp1)
    comp3 = Train(comp2, trial, epoch, batchsize, embeddim, hiddendim, dropout, spdropout, trainsequencelength)
    comp4 = Eval(comp3, trial, epoch, batchsize, embeddim, hiddendim, dropout, spdropout, trainsequencelength)

if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(passing_parameter, __file__[:-3]+ '.yaml')
