{
  global: {
    // User-defined global parameters; accessible to all component and environments, Ex:
    // replicas: 4,
  },
  components: {
    // Component-level parameters, defined initially from 'ks prototype use ...'
    // Each object below should correspond to a component in the components/ directory
    "t2t-job": {
      numWorker: 1,
      numMaster: 1,
      numPs: 1,
      numWorkerGpu: 0,
      numPsGpu: 0,

      train_steps: 100,
      eval_steps: 10,

      image: "gcr.io/kubeflow-dev/code-search:devel",
      imageGpu: "gcr.io/kubeflow-dev/code-search:gpu-devel",
      imagePullSecrets: [],
    },

    "t2t-gh-summarizer": {
      "name": "github_function_summarizer",
      "problem": "github_function_summarizer",
      "dataDir": "gs://kubeflow-dev/code-search/raw_data",
      "outputDir": "gs://kubeflow-dev/code-search/train",
      "model": "transformer",
      "hparams_set": "transformer_base"
    },
  },
}
