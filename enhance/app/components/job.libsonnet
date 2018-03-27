local k = import "k.libsonnet";

{
  parts:: {
    job(name, namespace, image, command, restartPolicy, backoffLimit):: {
      apiVersion: "batch/v1",
      kind: "Job",
      metadata: {
        name: name,
        namespace: namespace,
      },
      spec: {
        template: {
          spec: {
            containers: [
              {
                name: name,
                image: image,
                command: command
              },
            ],
            restartPolicy: restartPolicy,
          },
        },
        backoffLimit: backoffLimit,
      },
    },
  },
}