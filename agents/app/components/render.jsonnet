local params = std.extVar("__ksonnet/params").components["render"];
local k = import 'k.libsonnet';
local deployment = k.extensions.v1beta1.deployment;
local container = deployment.mixin.spec.template.spec.containersType;
local podTemplate = k.extensions.v1beta1.podTemplate;

local tfJob = import 'kubeflow/tf-job/tf-job.libsonnet';

local name = params.name;
local namespace = params.namespace;
local num_gpus = params.num_gpus;
local log_dir = params.log_dir;
local imageGpu = "";
local image = params.image;
local numCpu = params.num_cpu;

local args = [
  "--run_mode=render",
  "--logdir=" + log_dir,
  "--num_agents=1"
];

local workerSpec = if num_gpus > 0 then
  	tfJob.parts.tfJobReplica("MASTER", 1, args, imageGpu, num_gpus)
  	else
  	tfJob.parts.tfJobReplica("MASTER", 1, args, image);

local nfsClaimName = params.nfs_claim_name;

local replicas = std.map(function(s)
  s + {
    template+: {
      spec+:  {
        containers: [
          s.template.spec.containers[0] + {
            resources: {
              limits: {
                cpu: numCpu
              },
              requests: {
                cpu: numCpu
              }
            },
            volumeMounts:[{
              name: "nfs",
              mountPath: "/mnt/" + nfsClaimName
            }]
          },
        ],
        volumes: [{
          name: "nfs",
          persistentVolumeClaim: {
            claimName: nfsClaimName
          }
        }]
      },
    },
  },
  std.prune([workerSpec]));

local job = tfJob.parts.tfJob(name, namespace, replicas);

std.prune(k.core.v1.list.new([job]))
