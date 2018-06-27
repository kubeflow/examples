local baseParams = std.extVar("__ksonnet/params").components["nmslib"];

{

  nmsContainer(params, env):: {
    apiVersion: "extensions/v1beta1",
    kind: "Deployment",
    metadata: {
      name: params.name + "-deployment",
      namespace: env.namespace,
      labels: {
        app: params.name,
      }
    },
    spec: {
      replicas: params.replicas,
      selector: {
        matchLabels: {
          app: params.name,
        },
      },
      template: {
        metadata: {
          labels: {
            app: params.name,
          }
        },
        spec: {
          containers: [
            {
              name: params.name,
              image: params.image,
              args: params.args,
              ports: [
                {
                  containerPort: 8008,
                }
              ],
            }
          ],
        },
      },
    },
  },

  service(params, env):: {
    apiVersion: "v1",
    kind: "Service",
    metadata: {
      labels: {
        app: params.name,
      },
      name: params.name,
      namespace: env.namespace,
      annotations: {
        "getambassador.io/config":
          std.join("\n", [
            "---",
            "apiVersion: ambassador/v0",
            "kind: Mapping",
            "name: http-mapping-" + params.name,
            "prefix: /code-search/",
            "rewrite: /",
            "method: GET",
            "service: " + params.name + "." + env.namespace + ":8008",
          ]),
      },
    },
    spec: {
      type: "ClusterIP",
      selector: {
        app: params.name,
      },
      ports: [
        {
          name: "nmslib-serve-http",
          port: 8008,
          targetPort: 8008,
        },
      ],
    },
  },

  parts(newParams, env):: {
    local params = baseParams + newParams,

    creator:: {
      local creatorParams = params + {
        args: [
          "nmslib-create",
          "--data-file=" + params.dataFile,
          "--index-file=" + params.indexFile,
        ],
      },

      all: [
        $.nmsContainer(creatorParams, env),
      ],
    }.all,

    server:: {
      local serverParams = params + {
        args: [
          "nmslib-serve",
          "--data-file=" + params.dataFile,
          "--index-file=" + params.indexFile,
          "--problem=" + params.problem,
          "--data-dir=" + params.dataDir,
          "--serving-url=" + params.servingUrl,
        ],
      },

      all: [
        $.service(serverParams, env),
        $.nmsContainer(serverParams, env),
      ],
    }.all,
  }
}
