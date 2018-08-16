{
  parts(params, env):: [
    {
      apiVersion: "apps/v1",
      kind: "DaemonSet",
      metadata: {
        name: "prepull-jupyter-daemon",
        namespace: env.namespace,
      },
      spec: {
        selector: {
          matchLabels: {
            name: "prepull-jupyter-daemon",
          }
        },
        template: {
          metadata: {
            labels: {
              name: "prepull-jupyter-daemon"
            }
          },
          spec: {
            containers: [
              {
                name: image.name,
                image: image.image,
                command: ["sh", "-c", "tail -f /dev/null"],
              }
              for image in params.imageList
            ]
          }
        }
      },
    },
  ],
}
