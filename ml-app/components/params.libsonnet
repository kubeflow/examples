{
  global: {
    // User-defined global parameters; accessible to all component and environments, Ex:
    // replicas: 4,
  },
  components: {
    // Component-level parameters, defined initially from 'ks prototype use ...'
    // Each object below should correspond to a component in the components/ directory
    "kubeflow-core": {
      cloud: "null",
      disks: "null",
      name: "kubeflow-core",
      namespace: "default",
      tfJobImage: "gcr.io/tf-on-k8s-dogfood/tf_operator:v20171214-0bd02ac",
    },
    "agents": {
      algorithm: "agents.algorithms.ppo.ppo.PPO",
      data_dir: "/tmp/t2t_data_dir/",
      discount: 0.995,
      dump_dependency_versions: "False",
      env: "KukaBulletEnv-v0",
      eval_episodes: 25,
      gcp_project: "kubeflow-rl",
      generate_data: "True",
      hparam_set_id: "pybullet_kuka_ff",
      image: "gcr.io/kubeflow-rl/agents:agents-0202-1020-01ec",
      image_gpu: "null",
      init_logstd: "-1",
      init_mean_factor: 0.1,
      job_tag: "0202-1053-3a98",
      kl_cutoff_coef: 1000,
      kl_cutoff_factor: 2,
      kl_init_penalty: 1,
      kl_target: 0.01,
      learning_rate: 0.0001,
      logdir: "gs://kubeflow-rl-kf/jobs/pybullet-kuka-0202-1053-3a98",
      max_length: 1000,
      name: "render-0202-1054-9dfa",
      namespace: "rl",
      network: "agents.scripts.networks.feed_forward_gaussian",
      num_agents: 30,
      num_cpu: 1,
      num_gpus: 0,
      num_masters: 1,
      num_ps: 1,
      num_replicas: 1,
      num_workers: 1,
      optimizer: "tensorflow.train.AdamOptimizer",
      output_dir: "/tmp/t2t_output_dir/",
      render_secs: 600,
      run_base_tag: "0e90193e",
      run_mode: "render",
      save_checkpoints_secs: 30,
      steps: 40000000,
      sync_replicas: "False",
      train_steps: 100,
      update_epochs: 25,
      update_every: 30,
    },
    tensorboard: {
      log_dir: "gs://kubeflow-rl-kf/jobs/pybullet-kuka-0123-1053-4837",
      name: "pybullet-kuka-0123-1053-4837",
      namespace: "rl",
      secret: "gcp-credentials",
      secret_file_name: "secret.json",
    },
  },
}
