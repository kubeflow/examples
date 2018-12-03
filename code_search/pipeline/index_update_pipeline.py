from typing import Dict
import uuid
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

def dataflow_preprocess_op(
        cluster_name: str,
        data_dir: 'GcsUri',
        failed_tokenize_bq_table: str,
        namespace: str,
        num_workers: int,
        project: 'GcpProject',
        token_pairs_bq_table: str,
        worker_machine_type: str,
        workflow_id: str,
        working_dir: str):
  return default_gcp_op(
    name='dataflow_preprocess',
    image='gcr.io/kubeflow-examples/code-search/ks:v20181203-a0c87ff-dirty-a99477',
    command=['/usr/local/src/submit_preprocess_job.sh'],
    arguments=[
      "--cluster=%s" % cluster_name,
      "--dataDir=%s" % data_dir,
      "--failedTokenizeBQTable=%s" % failed_tokenize_bq_table,
      "--namespace=%s" % namespace,
      "--numWorkers=%s" % num_workers,
      "--project=%s" % project,
      "--tokenPairsBQTable=%s" % token_pairs_bq_table,
      "--workerMachineType=%s" % worker_machine_type,
      "--workflowId=%s" % workflow_id,
      "--workingDir=%s" % working_dir,
      "--vocabularyFile=%s" % 'gs://code-search-demo/20181104/data/vocab.kf_github_function_docstring.8192.subwords',
    ]
  )

def dataflow_function_embedding_op(
        cluster_name: str,
        data_dir: 'GcsUri',
        function_embeddings_bq_table: str,
        function_embeddings_dir: str,
        namespace: str,
        num_workers: int,
        project: 'GcpProject',
        saved_model_dir: 'GcsUri',
        token_pairs_bq_table: str,
        worker_machine_type: str,
        workflow_id: str,
        working_dir: str,):
  return default_gcp_op(
    name='dataflow_function_embedding',
    image='gcr.io/kubeflow-examples/code-search/ks:v20181203-a0c87ff-dirty-a99477',
    command=['/usr/local/src/submit_code_embeddings_job.sh'],
    arguments=[
      "--cluster=%s" % cluster_name,
      "--dataDir=%s" % data_dir,
      "--functionEmbeddingsDir=%s" % function_embeddings_dir,
      "--functionEmbeddingsBQTable=%s" % function_embeddings_bq_table,
      "--modelDir=%s" % saved_model_dir,
      "--namespace=%s" % namespace,
      "--numWorkers=%s" % num_workers,
      "--project=%s" % project,
      "--tokenPairsBQTable=%s" % token_pairs_bq_table,
      "--workerMachineType=%s" % worker_machine_type,
      "--workflowId=%s" % workflow_id,
      "--workingDir=%s" % working_dir,
    ]
  )


def search_index_creator_op(
        cluster_name: str,
        function_embeddings_dir: str,
        index_file: str,
        lookup_file: str,
        namespace: str,
        workflow_id: str):
  return dsl.ContainerOp(
    # use component name as step name
    name='search_index_creator',
    image='gcr.io/kubeflow-examples/code-search/ks:v20181203-a0c87ff-dirty-a99477',
    command=['/usr/local/src/launch_search_index_creator_job.sh'],
    arguments=[
      '--cluster=%s' % cluster_name,
      '--functionEmbeddingsDir=%s' % function_embeddings_dir,
      '--indexFile=%s' % index_file,
      '--lookupFile=%s' % lookup_file,
      '--namespace=%s' % namespace,
      '--workflowId=%s' % workflow_id,
    ]
  )


def update_index_op(
        app_dir: str,
        base_branch: str,
        base_git_repo: str,
        bot_email: str,
        fork_git_repo: str,
        index_file: str,
        lookup_file: str,
        workflow_id: str):
  return (
    dsl.ContainerOp(
      name='update_index',
      image='gcr.io/kubeflow-examples/code-search/ks:v20181203-a0c87ff-dirty-a99477',
      command=['/usr/local/src/update_index.sh'],
      arguments=[
        '--appDir=%s' % app_dir,
        '--baseBranch=%s' % base_branch,
        '--baseGitRepo=%s' % base_git_repo,
        '--botEmail=%s' % bot_email,
        '--forkGitRepo=%s' % fork_git_repo,
        '--indexFile=%s' % index_file,
        '--lookupFile=%s' % lookup_file,
        '--workflowId=%s' % workflow_id,
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
    saved_model_dir='gs://code-search-demo/models/20181107-dist-sync-gpu/export/1541712907/',
    target_dataset='code_search',
    worker_machine_type='n1-highcpu-32',
    num_workers=5,
    base_git_repo='kubeflow/examples',
    base_branch='master',
    app_dir='code_search/ks-web-app',
    fork_git_repo='IronPan/examples',
    bot_email='kf.sample.bot@gmail.com'):
  workflow_name = '{{workflow.name}}'
  # Can't use workflow name as bq_suffix since BQ table doesn't accept '-' and
  # workflow name is assigned at runtime. Pipeline might need to support
  # replacing characters in workflow name.
  bq_suffix = uuid.uuid4().hex[:6].upper()
  working_dir = '%s/%s' % (working_dir, workflow_name)
  data_dir = '%s/%s/' % (working_dir, "data")
  lookup_file = '%s/code-embeddings-index/embedding-to-info.csv' % working_dir
  index_file = '%s/code-embeddings-index/embeddings.index'% working_dir
  function_embeddings_dir = '%s/%s' % (working_dir, "code_embeddings")
  token_pairs_bq_table = '%s:%s.token_pairs_%s' %(project, target_dataset, bq_suffix)
  failed_tokenize_bq_table = '%s:%s.failed_tokenize_%s' %(project, target_dataset, bq_suffix)
  function_embeddings_bq_table = \
    '%s:%s.function_embeddings_%s' % (project, target_dataset, bq_suffix)

  preprocess = dataflow_preprocess_op(
    cluster_name,
    data_dir,
    failed_tokenize_bq_table,
    namespace,
    num_workers,
    project,
    token_pairs_bq_table,
    worker_machine_type,
    workflow_name,
    working_dir)

  function_embedding = dataflow_function_embedding_op(
    cluster_name,
    data_dir,
    function_embeddings_bq_table,
    function_embeddings_dir,
    namespace,
    num_workers,
    project,
    saved_model_dir,
    token_pairs_bq_table,
    worker_machine_type,
    workflow_name,
    working_dir)
  function_embedding.after(preprocess)

  search_index_creator = search_index_creator_op(
    cluster_name,
    function_embeddings_dir,
    index_file,
    lookup_file,
    namespace,
    workflow_name)
  search_index_creator.after(function_embedding)

  update_index_op(
    app_dir,
    base_branch,
    base_git_repo,
    bot_email,
    fork_git_repo,
    index_file,
    lookup_file,
    workflow_name).after(search_index_creator)


if __name__ == '__main__':
  import kfp.compiler as compiler

  compiler.Compiler().compile(function_embedding_update, __file__ + '.tar.gz')
