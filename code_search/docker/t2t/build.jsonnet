// TODO(jlewi): We should tag the image latest and then
// use latest as a cache so that rebuilds are fast
// https://cloud.google.com/cloud-build/docs/speeding-up-builds#using_a_cached_docker_image
{
	
	"steps": [
    {
      "name": "gcr.io/cloud-builders/docker",
      "args": ["build", "-t", "gcr.io/kubeflow-examples/code-search:" + std.extVar("tag"), 
             	 "--label=git-versions=" + std.extVar("gitVersion"), 
               "--build-arg", "BASE_IMAGE_TAG=1.11.0",
               "--file=docker/t2t/Dockerfile", "."],
      "waitFor": ["-"],
    },
    {
      "name": "gcr.io/cloud-builders/docker",
      "args": ["build", "-t", "gcr.io/kubeflow-examples/code-search-gpu:" + std.extVar("tag"), 
             	 "--label=git-versions=" + std.extVar("gitVersion"), 
               "--build-arg", "BASE_IMAGE_TAG=1.11.0-gpu",
               "--file=docker/t2t/Dockerfile", "."],
      "waitFor": ["-"],
    },
    {
      "name": "gcr.io/cloud-builders/docker",
      "args": ["build", "-t", "gcr.io/kubeflow-examples/code-search-dataflow:" + std.extVar("tag"), 
               "--label=git-versions=" + std.extVar("gitVersion"),
               "--file=docker/t2t/Dockerfile.dataflow", "."],
      "waitFor": ["-"],
    },
  ],
  "images": ["gcr.io/kubeflow-examples/code-search:" + std.extVar("tag"), 
             "gcr.io/kubeflow-examples/code-search-gpu:" + std.extVar("tag"),
             "gcr.io/kubeflow-examples/code-search-dataflow:" + std.extVar("tag")],
}