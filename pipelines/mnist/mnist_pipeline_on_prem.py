#!/usr/bin/env python3

import kfp.dsl as dsl
from kubernetes import client as k8s_client


def mnist_train_op(tf_data_dir: str, tf_model_dir: str,
                   tf_export_dir: str, train_steps: int, batch_size: int,
                   learning_rate: float, step_name='Training'):
    return dsl.ContainerOp(
        name=step_name,
        image='docker.io/jinchi/mnist_model:0.2',
        arguments=[
            '/opt/model.py',
            '--tf-data-dir', tf_data_dir,
            '--tf-model-dir', tf_model_dir,
            '--tf-export-dir', tf_export_dir,
            '--tf-train-steps', train_steps,
            '--tf-batch-size', batch_size,
            '--tf-learning-rate', learning_rate,
        ],
        file_outputs={'export': '/tf_export_dir.txt'}
    )


def kubeflow_deploy_op(tf_export_dir:str, server_name: str, pvc_name: str, step_name='Deploy_serving'):
    return dsl.ContainerOp(
        name=step_name,
        image='gcr.io/ml-pipeline/ml-pipeline-kubeflow-deployer:7775692adf28d6f79098e76e839986c9ee55dd61',
        arguments=[
            '--cluster-name', 'mnist-pipeline',
            '--model-export-path', tf_export_dir,
            '--server-name', server_name,
            '--pvc-name', pvc_name,
        ]
    )


@dsl.pipeline(
    name='Mnist Pipelines for on-prem cluster',
    description='Mnist Pipelines for on-prem cluster'
)
def mnist_pipeline(
        model_name='mnist',
        pvc_name='mnist-pvc',
        tf_data_dir='data',
        tf_model_dir='model',
        tf_export_dir='model/export',
        batch_size=100,
        training_steps=200,
        learning_rate=0.01):
    mnist_training = mnist_train_op('/mnt/%s' % tf_data_dir, '/mnt/%s' % tf_model_dir, '/mnt/%s' % tf_export_dir,
                                    training_steps, batch_size, learning_rate).add_volume(
        k8s_client.V1Volume(name='mnist-nfs', persistent_volume_claim=k8s_client.V1PersistentVolumeClaimVolumeSource(
            claim_name='mnist-pvc'))).add_volume_mount(k8s_client.V1VolumeMount(mount_path='/mnt', name='mnist-nfs'))
    deploy_serving = kubeflow_deploy_op(mnist_training.output, model_name, pvc_name).add_volume_mount(
        k8s_client.V1VolumeMount(mount_path='/mnt', name='mnist-nfs'))


if __name__ == '__main__':
    import kfp.compiler as compiler

    compiler.Compiler().compile(mnist_pipeline, __file__ + '.tar.gz')
