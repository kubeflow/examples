from typing import Dict
from kubernetes import client as k8s_client
import kfp.dsl as dsl


# disable max arg lint check
# pylint: disable=R0913


def default_gcp_op(name: str, image: str, command: str = None,
           arguments: str = None, file_inputs: Dict[dsl.PipelineParam, str] = None,
           file_outputs: Dict[str, str] = None, is_exit_handler=False):
  """An operator that mounts the default GCP service account to the container.

  The user-gcp-sa secret is created as part of the kubeflow deployment that
  stores the access token for kubeflow user service account.

  With this service account, the container has a range of GCP APIs to
  access to. This service account is automatically created as part of the
  kubeflow deployment.

  For the list of the GCP APIs this service account can access to, check
  https://github.com/kubeflow/kubeflow/blob/7b0db0d92d65c0746ac52b000cbc290dac7c62b1/deployment/gke/deployment_manager_configs/iam_bindings_template.yaml#L18

  If you want to call the GCP APIs in a different project, grant the kf-user
  service account access permission.
  """

  return (
    dsl.ContainerOp(
      name,
      image,
      command,
      arguments,
      file_inputs,
      file_outputs,
      is_exit_handler,
    )
      .add_volume(
      k8s_client.V1Volume(
        name='gcp-credentials',
        secret=k8s_client.V1SecretVolumeSource(
          secret_name='user-gcp-sa'
        )
      )
    )
      .add_volume_mount(
      k8s_client.V1VolumeMount(
        mount_path='/secret/gcp-credentials',
        name='gcp-credentials',
      )
    )
      .add_env_variable(
      k8s_client.V1EnvVar(
        name='GOOGLE_APPLICATION_CREDENTIALS',
        value='/secret/gcp-credentials/user-gcp-sa.json'
      )
    )
  )

def dataflow_function_embedding_op(
        project: 'GcpProject', cluster_name: str, target_dataset: str, data_dir: 'GcsUri',
        saved_model_dir: 'GcsUri', workflow_id: str, worker_machine_type: str,
        num_workers: int, working_dir: str, step_name='dataflow_function_embedding'):
  return default_gcp_op(
    name=step_name,
    image='gcr.io/kubeflow-examples/code-search-ks:v20181127-08f8c05-dirty-19ca4c',
    command=['/usr/local/src/submit_code_embeddings_job.sh'],
    arguments=[
      "--workflowId=%s" % workflow_id,
      "--modelDir=%s" % saved_model_dir,
      "--dataDir=%s" % data_dir,
      "--numWorkers=%s" % num_workers,
      "--project=%s" % project,
      "--targetDataset=%s" % target_dataset,
      "--workerMachineType=%s" % worker_machine_type,
      "--workingDir=%s" % working_dir,
      '--cluster=%s' % cluster_name,
    ]
  )


def search_index_creator_op(
        working_dir: str, data_dir: str, workflow_id: str, cluster_name: str, namespace: str):
  return dsl.ContainerOp(
    # use component name as step name
    name='search_index_creator',
    image='gcr.io/kubeflow-examples/code-search-ks:v20181127-08f8c05-dirty-19ca4c',
    command=['/usr/local/src/launch_search_index_creator_job.sh'],
    arguments=[
      '--workingDir=%s' % working_dir,
      '--dataDir=%s' % data_dir,
      '--workflowId=%s' % workflow_id,
      '--cluster=%s' % cluster_name,
      '--namespace=%s' % namespace,
    ]
  )


# The pipeline definition
@dsl.pipeline(
  name='function_embedding',
  description='Example function embedding pipeline'
)
def function_embedding_update(
    project,
    working_dir,
    saved_model_dir,
    cluster_name,
    namespace,
    target_dataset=dsl.PipelineParam(name='target-dataset', value='code_search'),
    worker_machine_type=dsl.PipelineParam(name='worker-machine-type', value='n1-highcpu-32'),
    num_workers=dsl.PipelineParam(name='num-workers', value=5)):
  workflow_name = '{{workflow.name}}'
  working_dir = '%s/%s' % (working_dir, workflow_name)
  data_dir = '%s/data' % working_dir
  function_embedding = dataflow_function_embedding_op(
                            project, cluster_name, target_dataset, data_dir,
                            saved_model_dir,
                            workflow_name, worker_machine_type, num_workers, working_dir)
  search_index_creator_op(
      working_dir, data_dir, workflow_name, cluster_name, namespace).after(function_embedding)


if __name__ == '__main__':
  import kfp.compiler as compiler

  compiler.Compiler().compile(function_embedding_update, __file__ + '.tar.gz')
