{
  parts(params):: {
    apiVersion: "kubeflow.org/v1alpha1",
    kind: "TFJob",
    metadata: {
      name: "tensor2tensor",
      namespace: params.namespace,
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
                  command: [
                    "bash",
                  ],
                  args: [
                    "/home/jovyan/train_dist_launcher.sh",
                    "1",
                    params.workers,
                    "0",
                    params.train_steps,
                    "/job:master",
                    "False",
                  ],
                },
              ],
              restartPolicy: "OnFailure",
            },
          },
          tfReplicaType: "MASTER",
        },
        {
          replicas: params.workers,
          template: {
            spec: {
              containers: [
                {
                  image: params.image,
                  name: "tensorflow",
                  command: [
                    "bash",
                  ],
                  args: [
                    "/home/jovyan/train_dist_launcher.sh",
                    "1",
                    params.workers,
                    "0",
                    params.train_steps,
                    "/job:master",
                    "False",
                  ],
                },
              ],
              restartPolicy: "OnFailure",
            },
          },
          tfReplicaType: "WORKER",
        },
        {
          replicas: 1,
          template: {
            spec: {
              containers: [
                {
                  image: params.image,
                  name: "tensorflow",
                  command: [
                    "bash",
                  ],
                  args: [
                    "/home/jovyan/ps_dist_launcher.sh",
                  ],
                },
              ],
              restartPolicy: "OnFailure",
            },
          },
          tfReplicaType: "PS",
        },
      ],
      terminationPolicy: {
        chief: {
          replicaIndex: 0,
          replicaName: "MASTER",
        },
      },
    },
  },
}
