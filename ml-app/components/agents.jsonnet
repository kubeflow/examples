local params = std.extVar("__ksonnet/params").components["agents"];
local k = import 'k.libsonnet';
local deployment = k.extensions.v1beta1.deployment;
local container = deployment.mixin.spec.template.spec.containersType;
local podTemplate = k.extensions.v1beta1.podTemplate;

local tfJob = import 'kubeflow/tf-job/tf-job.libsonnet';

local name = params.name;
local namespace = params.namespace;
local num_gpus = params.num_gpus;
local hparam_set_id = params.hparam_set_id;
local gcp_project = params.gcp_project;
local jobTag = params.job_tag;
local logDir = params.log_dir;
local image = params.image;
local imageGpu = params.image_gpu;
local numCpu = params.num_cpu;
local dumpDependencyVersions = params.dump_dependency_versions;
local runMode = params.run_mode;
local logdir = params.logdir;
local hparamSetID = params.hparam_set_id;
local runBaseTag = params.run_base_tag;
local syncReplicas = params.sync_replicas;
local numGpus = params.num_gpus;
local algorithm = params.algorithm;
local numAgents = params.num_agents;
local evalEpisodes = params.eval_episodes;
local env = params.env;
local maxLength = params.max_length;
local steps = params.steps;
local network = params.network;
local initMeanFactor = params.init_mean_factor;
//local initLogstd = params.init_logstd;
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
  "--run_mode=" + runMode,
  "--logdir=" + logdir,
  "--hparam_set_id=" + hparamSetID,
  "--run_base_tag=" + runBaseTag,
  "--sync_replicas=" + syncReplicas,
  "--num_gpus=" + numGpus,
  "--algorithm=" + algorithm,
  "--num_agents=" + numAgents,
  "--eval_episodes=" + evalEpisodes,
  "--env=" + env,
  "--max_length=" + maxLength,
  "--steps=" + steps,
  "--network=" + network,
  //"--policy_layers=" + policyLayers,
  //"--value_layers=" + valueLayers,
  "--init_mean_factor=" + initMeanFactor,
//  "--init_logstd=" + initLogstd,
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

local workerSpec = if numGpus > 0 then
  	tfJob.parts.tfJobReplica("MASTER", 1, args, imageGpu, numGpus)
  	else
  	tfJob.parts.tfJobReplica("MASTER", 1, args, image);

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
          },
        ],
      },
    },
  },
  std.prune([workerSpec]));

local job = tfJob.parts.tfJob(name, namespace, replicas);

std.prune(k.core.v1.list.new([job]))
