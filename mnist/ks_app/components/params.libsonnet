{
  global: {},
  components: {
    train: {
      batchSize: 100,
      envVariables: 'GOOGLE_APPLICATION_CREDENTIALS=/var/secrets/user-gcp-sa.json',
      exportDir: 'gs://kubeflow-ci_temp/mnist-jlewi',
      image: 'gcr.io/kubeflow-examples/mnist/model:v20190108-v0.2-137-g38daafa-dirty-911944',
      learningRate: '0.01',
      modelDir: 'gs://kubeflow-ci_temp/mnist-jlewi',
      name: 'mnist-train',
      numPs: 1,
      numWorkers: 2,
      secret: '',
      trainSteps: 200,
    },
  },
}