// Train the model reading & writing the data from a PVC.
local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["tfjob-pvc"];
local k = import "k.libsonnet";

local tfjob = {
    apiVersion: "kubeflow.org/v1alpha1",
    kind: "TFJob",
    metadata: {
      name: "tf-job-issue-summarization-pvc",
      namespace: env.namespace,
    },
    spec: {
      replicaSpecs: [
        {
          replicas: 1,
          template: {
            spec: {
              containers: [
                {
                  image: params.image,
                  name: "tensorflow",
                  volumeMounts: [
                    {
                      name: "data",
                      mountPath: "/data",                    
                    },
                  ],
                  command: [
                    "python",
                    "/workdir/train.py",
                    "--sample_size=" + std.toString(params.sample_size),
                    "--input_data=" + params.input_data,
                    "--output_model=" + params.output_model,                    
                  ],
                },
              ],
              volumes: [
                    {
		            name: "data",
		            persistentVolumeClaim: {
		              claimName: "data-pvc",
		            },
		          },
              ],
              restartPolicy: "OnFailure",
            },
          },
          tfReplicaType: "MASTER",
        },
      ],
      terminationPolicy: {
        chief: {
          replicaIndex: 0,
          replicaName: "MASTER",
        },
      },
    },
  };

std.prune(k.core.v1.list.new([tfjob]))
