local baseParams = std.extVar("__ksonnet/params").components["nmslib"];

{
  spec(params, env, apiVersion="extensions/v1beta1", kind="Deployment"):: {
    apiVersion: apiVersion,
    kind: kind,
    metadata: {
      name: params.name,
      namespace: env.namespace,
      labels: {
        app: params.name,
      }
    },
    spec: {
      replicas: params.replicas,
      [if kind == "Deployment" then "selector"]: {
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
          [if kind == "Job" then "restartPolicy"]: "OnFailure",
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
              env: [
                {
                  name: "GOOGLE_APPLICATION_CREDENTIALS",
                  value: "/secret/gcp-credentials/user-gcp-sa.json",
                }
              ],
              volumeMounts: [
                {
                  mountPath: "/secret/gcp-credentials",
                  name: "gcp-credentials",
                },
              ],
            }
          ],
          volumes: [
            {
              name: "gcp-credentials",
              secret: {
                secretName: "user-gcp-sa",
              },
            },
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
          "-m",
          "code_search.nmslib.cli.create_search_index",
          "--data_dir=" + params.dataDir,
          "--lookup_file=" + params.lookupFile,
          "--index_file=" + params.indexFile,
        ],
      },

      all: [
        $.spec(creatorParams, env, apiVersion="batch/v1", kind="Job"),
      ],
    }.all,

    server:: {
      local serverParams = params + {
        args: [
          "-m",
          "code_search.nmslib.cli.start_search_server",
          "--problem=" + params.problem,
          "--data_dir=" + params.dataDir,
          "--lookup_file=" + params.lookupFile,
          "--index_file=" + params.indexFile,
          "--serving_url=" + params.servingUrl,
        ],
      },

      all: [
        $.service(serverParams, env),
        $.spec(serverParams, env),
      ],
    }.all,
  }
}
