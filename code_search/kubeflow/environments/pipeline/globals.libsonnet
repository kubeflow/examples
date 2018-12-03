{
  // Warning: Do not define a global "image" as that will end up overriding
  // the image parameter for all components. Define more specific names
  // e.g. "dataflowImage", "trainerCpuImage", "trainerGpuImage",
  experiment: "pipeline",
  waitUntilFinish: "true",
  readGithubDatasetForFunctionEmbedding: "true",
}
