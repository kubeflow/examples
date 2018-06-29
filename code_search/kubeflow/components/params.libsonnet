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

      image: "gcr.io/kubeflow-dev/code-search:v20180621-266e689",
      imageGpu: "gcr.io/kubeflow-dev/code-search:v20180621-gpu-db4f1ee",
      imagePullSecrets: [],

      dataDir: "null",
      outputDir: "null",
      model: "null",
      hparams_set: "null",

      // TODO(sanyamkapoor): A workaround for tensorflow/tensor2tensor#879
      gsDataDir: "null",
      gsOutputDir: "null",
    },

    "nmslib": {
      name: null,
      replicas: 1,
      image: "gcr.io/kubeflow-dev/code-search:v20180621-266e689",

      dataFile: null,
      indexFile: null,
      problem: null,
      dataDir: null,
      servingUrl: null,
    },

    "t2t-translate-datagen": {
      jobType: "datagen",

      name: "translate-ende-wmt32k-datagen",
      problem: "translate_ende_wmt32k",

      // TODO(sanyamkapoor): A workaround for tensorflow/tensor2tensor#879
      dataDir: "/data",
      outputDir: "/data",
      gsOutputDir: "gs://kubeflow-examples/t2t-translate/translate_ende_wmt32k/datagen",
    },

    "t2t-translate-exporter": {
      jobType: "exporter",

      name: "translate-ende-wmt32k-exporter",
      problem: "translate_ende_wmt32k",
      dataDir: "gs://kubeflow-examples/t2t-translate/translate_ende_wmt32k/datagen",
      outputDir: "gs://kubeflow-examples/t2t-translate/translate_ende_wmt32k/output",
      model: "transformer",
      hparams_set: "transformer_base_single_gpu",
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
      dataDir: "gs://kubeflow-examples/t2t-translate/translate_ende_wmt32k/datagen",
      outputDir: "gs://kubeflow-examples/t2t-translate/translate_ende_wmt32k/output",
      model: "transformer",
      hparams_set: "transformer_base_single_gpu",
    },

    "t2t-translate-serving": {
      name: "t2t-translate",
      modelName: "t2t-translate",
      modelPath: "gs://kubeflow-examples/t2t-translate/translate_ende_wmt32k/output/export/Servo",
      modelServerImage: "gcr.io/kubeflow-images-public/tensorflow-serving-1.8:latest",
      cloud: "gcp",
      gcpCredentialSecretName: "gcp-credentials",
    },

    "nms-creator": {
      name: "nms-creator",
    },

    "nms-server": {
      name: "nms-server",
    },
  },
}
