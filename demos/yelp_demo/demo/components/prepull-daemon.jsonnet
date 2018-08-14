local env = std.extVar("__ksonnet/environments");
local k = import "k.libsonnet";
local params = {
  imageList: [
    {
      name: "1-4cpu",
      image: "gcr.io/kubeflow-images-public/tensorflow-1.4.1-notebook-cpu:v20180419-0ad94c4e",
    },
    {
      name: "1-4gpu",
      image: "gcr.io/kubeflow-images-public/tensorflow-1.4.1-notebook-gpu:v20180419-0ad94c4e",
    },
  ],
};


local daemon = import "prepull-daemon.libsonnet";
std.prune(k.core.v1.list.new(daemon.parts(params, env)))
