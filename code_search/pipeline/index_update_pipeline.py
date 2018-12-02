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
    image='gcr.io/kubeflow-examples/code-search/ks:v20181130-b807843',
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
        index_file: str, lookup_file: str, data_dir: str,
        workflow_id: str, cluster_name: str, namespace: str):
  return dsl.ContainerOp(
    # use component name as step name
    name='search_index_creator',
    image='gcr.io/kubeflow-examples/code-search/ks:v20181130-b807843',
    command=['/usr/local/src/launch_search_index_creator_job.sh'],
    arguments=[
      '--indexFile=%s' % index_file,
      '--lookupFile=%s' % lookup_file,
      '--dataDir=%s' % data_dir,
      '--workflowId=%s' % workflow_id,
      '--cluster=%s' % cluster_name,
      '--namespace=%s' % namespace,
    ]
  )


def update_index_op(
        base_git_repo: str, base_branch: str, app_dir: str, fork_git_repo: str,
        index_file: str, lookup_file: str, workflow_id: str, bot_email: str):
  return (
    dsl.ContainerOp(
      name='update_index',
      image='gcr.io/kubeflow-examples/code-search/ks:v20181130-b807843',
      command=['/usr/local/src/update_index.sh'],
      arguments=[
        '--baseGitRepo=%s' % base_git_repo,
        '--baseBranch=%s' % base_branch,
        '--appDir=%s' % app_dir,
        '--forkGitRepo=%s' % fork_git_repo,
        '--env=%s' % 'pipeline',
        '--indexFile=%s' % index_file,
        '--lookupFile=%s' % lookup_file,
        '--workflowId=%s' % workflow_id,
        '--botEmail=%s' % bot_email,
      ],
    )
    .add_volume(
      k8s_client.V1Volume(
        name='github-access-token',
        secret=k8s_client.V1SecretVolumeSource(
          secret_name='github-access-token'
        )
      )
    )
    .add_env_variable(
      k8s_client.V1EnvVar(
        name='GITHUB_TOKEN',
        value_from=k8s_client.V1EnvVarSource(
          secret_key_ref=k8s_client.V1SecretKeySelector(
            name='github-access-token',
            key='token',
          )
        )
      )
    )
  )


# The pipeline definition
@dsl.pipeline(
  name='function_embedding',
  description='Example function embedding pipeline'
)
def function_embedding_update(
    project='code-search-demo',
    cluster_name='cs-demo-1103',
    namespace='kubeflow',
    working_dir='gs://code-search-demo/pipeline',
    data_dir='gs://code-search-demo/20181104/data',
    saved_model_dir='gs://code-search-demo/models/20181107-dist-sync-gpu/export/1541712907/',
    target_dataset='code_search',
    worker_machine_type='n1-highcpu-32',
    function_embedding_num_workers=5,
    base_git_repo='kubeflow/examples',
    base_branch='master',
    app_dir='code_search/ks-web-app',
    fork_git_repo='IronPan/examples',
    bot_email='kf.sample.bot@gmail.com'):
  workflow_name = '{{workflow.name}}'
  working_dir = '%s/%s' % (working_dir, workflow_name)
  lookup_file = '%s/code-embeddings-index/embedding-to-info.csv' % working_dir
  index_file = '%s/code-embeddings-index/embeddings.index'% working_dir

  function_embedding = dataflow_function_embedding_op(
                            project, cluster_name, target_dataset, data_dir,
                            saved_model_dir, workflow_name, worker_machine_type,
                            function_embedding_num_workers, working_dir)

  search_index_creator = search_index_creator_op(
    index_file, lookup_file, data_dir, workflow_name, cluster_name, namespace)
  search_index_creator.after(function_embedding)
  update_index_op(
      base_git_repo, base_branch, app_dir, fork_git_repo,
      index_file, lookup_file, workflow_name, bot_email)\
    .after(search_index_creator)


if __name__ == '__main__':
  import kfp.compiler as compiler

  compiler.Compiler().compile(function_embedding_update, __file__ + '.tar.gz')
