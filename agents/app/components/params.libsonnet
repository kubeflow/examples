{
  global: {
  },
  components: {
    "train": {
      algorithm: "agents.ppo.PPOAlgorithm",
      discount: 0.995,
      dump_dependency_versions: "True",
      env: "KukaBulletEnv-v0",
      eval_episodes: 25,
      generate_data: "True",
      hparam_set_id: "pybullet_kuka_ff",
      image: "gcr.io/kubeflow-rl/agents:0405-1658-39bf",
      image_gpu: "null",
      init_mean_factor: 0.1,
      job_tag: "0206-1409-6174",
      kl_cutoff_coef: 1000,
      kl_cutoff_factor: 2,
      kl_init_penalty: 1,
      kl_target: 0.01,
      learning_rate: 0.0001,
      log_dir: "/mnt/nfs-1/train_dirs/studies/replicated-kuka-demo/kuka-0405-1707-545d",
      max_length: 1000,
      name: "kuka-0405-1707-545d",
      namespace: "kubeflow",
      network: "agents.scripts.networks.feed_forward_gaussian",
      nfs_claim_name: "nfs-1",
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
    "render": {
      image: "gcr.io/kubeflow-rl/agents:0319-1806-6614",
      log_dir: "/mnt/nfs-1/train_dirs/kubeflow-rl/studies/replicated-kuka-demo-1/kuka-0319-1735-222e",
      name: "render-0319-2043-47e6",
      namespace: "kubeflow",
      nfs_claim_name: "nfs-1",
      num_cpu: 4,
      num_gpus: 0,
    },
  },
}
