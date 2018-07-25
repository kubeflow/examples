{
  global: {},
  components: {
    // Component-level parameters, defined initially from 'ks prototype use ...'
    // Each object below should correspond to a component in the components/ directory
    model1: {
      cloud: 'gcp',
      deployHttpProxy: true,
      gcpCredentialSecretName: 'user-gcp-sa',
      modelPath: 'gs://kai-test2-models/object-detection',
      modelServerImage: 'gcr.io/kubeflow-images-public/tensorflow-serving-1.8gpu:latest',
      name: 'coco',
      numGpus: 1,
    },
  },
}
