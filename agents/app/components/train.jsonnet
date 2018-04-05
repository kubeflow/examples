local params = std.extVar("__ksonnet/params").components["train"];
local k = import 'k.libsonnet';
local deployment = k.extensions.v1beta1.deployment;
local container = deployment.mixin.spec.template.spec.containersType;
local podTemplate = k.extensions.v1beta1.podTemplate;

local tfJob = import 'kubeflow/tf-job/tf-job.libsonnet';

local name = params.name;
local namespace = params.namespace;
local num_gpus = params.num_gpus;
local hparam_set_id = params.hparam_set_id;
local jobTag = params.job_tag;
local image = params.image;
local imageGpu = params.image_gpu;
local numCpu = params.num_cpu;
local dumpDependencyVersions = params.dump_dependency_versions;
local log_dir = params.log_dir;
local hparamSetID = params.hparam_set_id;
local runBaseTag = params.run_base_tag;
local syncReplicas = params.sync_replicas;
local algorithm = params.algorithm;
local numAgents = params.num_agents;
local evalEpisodes = params.eval_episodes;
local env = params.env;
local maxLength = params.max_length;
local steps = params.steps;
local network = params.network;
local initMeanFactor = params.init_mean_factor;
local learningRate = params.learning_rate;
local optimizer = params.optimizer;
local updateEpochs = params.update_epochs;
local updateEvery = params.update_every;
local discount = params.discount;
local klTarget = params.kl_target;
local klCutoffFactor = params.kl_cutoff_factor;
local klCutoffCoef = params.kl_cutoff_coef;
local klInitPenalty = params.kl_init_penalty;

local renderSecs = params.render_secs;

local args = [
  "--run_mode=train",
  "--logdir=" + log_dir,
  "--hparam_set_id=" + hparamSetID,
  "--run_base_tag=" + runBaseTag,
  "--sync_replicas=" + syncReplicas,
  "--num_gpus=" + num_gpus,
  "--algorithm=" + algorithm,
  "--num_agents=" + numAgents,
  "--eval_episodes=" + evalEpisodes,
  "--env=" + env,
  "--max_length=" + maxLength,
  "--steps=" + steps,
  "--network=" + network,
  "--init_mean_factor=" + initMeanFactor,
  "--learning_rate=" + learningRate,
  "--optimizer=" + optimizer,
  "--update_epochs=" + updateEpochs,
  "--update_every=" + updateEvery,
  "--discount=" + discount,
  "--kl_target=" + klTarget,
  "--kl_cutoff_factor=" + klCutoffFactor,
  "--kl_cutoff_coef=" + klCutoffCoef,
  "--kl_init_penalty=" + klInitPenalty,
  "--dump_dependency_versions=" + dumpDependencyVersions,
  "--render_secs=" + renderSecs,
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
