{
	
	"steps": [
    {
      "name": "gcr.io/cloud-builders/docker",
      "args": ["build", "-t", "gcr.io/kubeflow-examples/code-search:" + std.extVar("tag"), 
             	"--label=git-versions=" + std.extVar("gitVersion"), 
                "--build-arg", "BASE_IMAGE_TAG=1.11.0",
      		   "./docker/t2t"],
    },
    {
      "name": "gcr.io/cloud-builders/docker",
      "args": ["build", "-t", "gcr.io/kubeflow-examples/code-search-gpu:" + std.extVar("tag"), 
             	"--label=git-versions=" + std.extVar("gitVersion"), 
                "--build-arg", "BASE_IMAGE_TAG=1.11.0-gpu",
      		   "./docker/t2t"],
    },
  ],
  "images": ["gcr.io/kubeflow-examples/code-search:" + std.extVar("tag"), 
             "gcr.io/kubeflow-examples/code-search-gpu:" + std.extVar("tag")],
}