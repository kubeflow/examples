local params = std.extVar("__ksonnet/params").components["train"];
local k = import 'k.libsonnet';
local deployment = k.extensions.v1beta1.deployment;
local container = deployment.mixin.spec.template.spec.containersType;
local podTemplate = k.extensions.v1beta1.podTemplate;

local tfJob = import 'kubeflow/tf-job/tf-job.libsonnet';

local args = [
  params.t2t_command,
  "--model=" + params.model,
  "--data_dir=" + params.data_root,
  "--tmp_dir=" + params.data_root,
  "--problems=" + params.problem,
  "--t2t_usr_dir=" + params.t2t_usr_dir,
  "--hparams_set=" + params.hparams_set,
  "--output_dir=" + params.train_dir,
  "--train_steps=" + params.train_steps,
  "--eval_steps=" + params.eval_steps,
  "--decode_hparams=" + params.decode_hparams,
  "--decode_from_file=" + params.decode_source_file,
  "--decode_to_file=" + params.decode_target_file,
];

local image = "gcr.io/kubeflow/tensorflow-notebook-cpu:latest";

local workerSpec = tfJob.parts.tfJobReplica("MASTER", 1, args, image);

local nfs_mount_path = "/mnt/" + params.nfs_claim;
local nfs_volume_name = "nfs-volume-mount";

local replicas = std.map(function(s)
  s + {
    template+: {
      spec+:  {
        volumes: [
          {
            name: nfs_volume_name,
            persistentVolumeClaim: {
                claimName: params.nfs_claim
            },
          },
        ],
        containers: [
          s.template.spec.containers[0] + {
            resources: {
              limits: {
                cpu: params.num_cpu
              },
              requests: {
                cpu: params.num_cpu
              }
            },
            // Attach the NFS data volume to each training container
            volumeMounts: [
              {
                name: nfs_volume_name,
                mountPath: nfs_mount_path,
              },
            ],
          },
        ],
      },
    },
  },
  std.prune([workerSpec]));

local job = tfJob.parts.tfJob(params.job_name, params.namespace, replicas);

std.prune(k.core.v1.list.new([job]))
