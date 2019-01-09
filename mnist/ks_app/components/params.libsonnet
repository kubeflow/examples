{
  global: {},
  components: {
    train: {      
      name: "mnist-train",
      image: "gcr.io/kubeflow-examples/mnist/model:v20190108-v0.2-137-g38daafa-dirty-911944",
	  modelDir: "/tmp/model",	  
	  exportDir: "/tmp/model",
	  trainSteps: "200",
	  batchSize: "100",	  
	  learningRate:"0.01",
	  envVariables: "",
	  // Running distributed requires a shared filesystem for the 
	  // checkpoints.
	  numWorkers: 0,
	  numPs: 0,
    },
  },
}