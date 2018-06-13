{
  global: {
    // User-defined global parameters; accessible to all component and environments, Ex:
    // replicas: 4,
  },
  components: {
    // Component-level parameters, defined initially from 'ks prototype use ...'
    // Each object below should correspond to a component in the components/ directory
    "t2tcpu": {
      args: "null",
      image: "null",
      image_gpu: "null",
      image_pull_secrets: "null",
      name: "t2tcpu",
      namespace: "null",
      num_gpus: 0,
      num_masters: 1,
      num_ps: 0,
      num_workers: 0,
    },
  },
}
