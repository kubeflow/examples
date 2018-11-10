#!/usr/bin/env python3

import kfp.dsl as kfp
import datetime

def training_op(learning_rate: float,
                num_layers: int,
                optimizer='ftrl',
                step_name='training'):
  return kfp.ContainerOp(
    name = step_name,
    image = 'katib/mxnet-mnist-example',
    command = ['python', '/mxnet/example/image-classification/train_mnist.py'],
    arguments = [
      '--batch-size', '64',
      '--lr', learning_rate,
      '--num-layers', num_layers,
      '--optimizer', optimizer,
    ]
  )

@kfp.pipeline(
  name='Pipeline GPU Example',
  description='Demonstrate the Kubeflow pipelines SDK with GPUs'
)

def kubeflow_training(
  learning_rate: kfp.PipelineParam=kfp.PipelineParam(name='learningrate', value=0.1),
  num_layers: kfp.PipelineParam=kfp.PipelineParam(name='numlayers', value='2'),
  optimizer: kfp.PipelineParam=kfp.PipelineParam(name='optimizer', value='ftrl')):
  training = training_op(learning_rate, num_layers, optimizer)

if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(kubeflow_training, __file__ + '.tar.gz')
