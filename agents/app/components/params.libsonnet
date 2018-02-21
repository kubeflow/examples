{
  global: {
    // User-defined global parameters; accessible to all component and environments, Ex:
    // replicas: 4,
  },
  components: {
    // Component-level parameters, defined initially from 'ks prototype use ...'
    // Each object below should correspond to a component in the components/ directory
    "agents": {
      algorithm: "agents.ppo.PPOAlgorithm",
      discount: 0.995,
      dump_dependency_versions: "True",
      env: "KukaBulletEnv-v0",
      eval_episodes: 25,
      generate_data: "True",
      hparam_set_id: "pybullet_kuka_ff",
      image: "gcr.io/kubeflow-rl/agents:0221-2315-5b40",
      image_gpu: "null",
      init_mean_factor: 0.1,
      job_tag: "0206-1409-6174",
      kl_cutoff_coef: 1000,
      kl_cutoff_factor: 2,
      kl_init_penalty: 1,
      kl_target: 0.01,
      learning_rate: 0.0001,
      log_dir: "gs://kubeflow-rl/studies/replicated-kuka-demo/kuka-0221-2329-afdd",
      max_length: 1000,
      name: "kuka-0221-2329-afdd",
      namespace: "rl",
      network: "agents.scripts.networks.feed_forward_gaussian",
      num_agents: 30,
      num_cpu: 30,
      num_gpus: 0,
      num_masters: 1,
      num_ps: 1,
      num_replicas: 1,
      num_workers: 1,
      optimizer: "tensorflow.train.AdamOptimizer",
      render_secs: 600,
      run_base_tag: "0e90193e",
      run_mode: "train",
      save_checkpoint_secs: 600,
      save_checkpoints_secs: 600,
      steps: 15000000,
      sync_replicas: "False",
      update_epochs: 25,
      update_every: 60,
    },
    "agents_render": {
      image: "gcr.io/kubeflow-rl/agents:0221-1635-d869",
      log_dir: "gs://kubeflow-rl/studies/replicated-kuka-demo/kuka-0221-1650-31dc",
      name: "render-0221-1705-4149",
      namespace: "rl",
      num_cpu: 4,
      num_gpus: 0,
    },
    tensorboard: {
      log_dir: "gs://kubeflow-rl/studies/replicated-kuka-demo",
      name: "tboard-0221-2330-5c5c",
      namespace: "rl",
      secret: "gcp-credentials",
      secret_file_name: "secret.json",
    },
  },
}
