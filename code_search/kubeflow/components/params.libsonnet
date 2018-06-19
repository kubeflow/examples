{
  global: {
    // User-defined global parameters; accessible to all component and environments, Ex:
    // replicas: 4,
  },
  components: {
    // Component-level parameters, defined initially from 'ks prototype use ...'
    // Each object below should correspond to a component in the components/ directory
    "t2t-job": {
      jobType: "trainer",

      numMaster: 1,
      numWorker: 0,
      numPs: 0,
      numWorkerGpu: 0,
      numPsGpu: 0,

      train_steps: 100,
      eval_steps: 10,

      image: "gcr.io/kubeflow-dev/code-search:devel",
      imageGpu: "gcr.io/kubeflow-dev/code-search:gpu-devel",
      imagePullSecrets: [],

      dataDir: "null",
      outputDir: "null",
      model: "null",
      hparams_set: "null",
    },

    "t2t-translate-datagen": {
      jobType: "datagen",

      name: "translate-ende-wmt32k-datagen",
      problem: "translate_ende_wmt32k",
      dataDir: "gs://kubeflow-dev/code_search/translate_ende_wmt32k/datagen",
    },

    "t2t-translate": {
      jobType: "trainer",
      numMaster: 1,
      numWorker: 2,
      numPs: 1,
      numWorkerGpu: 1,
      numPsGpu: 1,

      name: "translate-ende-wmt32k",
      problem: "translate_ende_wmt32k",
      dataDir: "gs://kubeflow-dev/code_search/translate_ende_wmt32k/datagen",
      outputDir: "gs://kubeflow-dev/code_search/translate_ende_wmt32k/output",
      model: "transformer",
      hparams_set: "transformer_base_single_gpu"
    },
  },
}
