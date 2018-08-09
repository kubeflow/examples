local baseParams = std.extVar("__ksonnet/params").components["nmslib"];

{
  deploymentSpec(params, env, containers, volumes=[]):: {
    apiVersion: "extensions/v1beta1",
    kind: "Deployment",
    metadata: {
      name: params.name,
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
          containers: containers,
          volumes: volumes,
        },
      },
    },
  },

  jobSpec(params, env, containers, volumes=[]):: {
    apiVersion: "batch/v1",
    kind: "Job",
    metadata: {
      name: params.name,
      namespace: env.namespace,
      labels: {
        app: params.name,
      }
    },
    spec: {
      replicas: params.replicas,
      template: {
        metadata: {
          labels: {
            app: params.name,
          }
        },
        spec: {
          "restartPolicy": "OnFailure",
          containers: containers,
          volumes: volumes,
        },
      },
    },
  },

  containerSpec(params, env=[], volumeMounts=[], ports=[]):: {
    name: params.name,
    image: params.image,
    args: params.args,
    ports: ports,
    env: env,
    volumeMounts: volumeMounts,
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

    local volumes = [
      {
        name: "gcp-credentials",
        secret: {
          secretName: "user-gcp-sa",
        },
      },
    ],

    local containerEnv = [
      {
        name: "GOOGLE_APPLICATION_CREDENTIALS",
        value: "/secret/gcp-credentials/user-gcp-sa.json",
      }
    ],

    local containerVolumeMounts = [
      {
        mountPath: "/secret/gcp-credentials",
        name: "gcp-credentials",
      },
    ],

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
        $.jobSpec(creatorParams, env,
                  [
                    $.containerSpec(creatorParams, env=containerEnv,
                                    volumeMounts=containerVolumeMounts)
                  ],
                  volumes=volumes),
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

      local containerPorts = [
        {
          containerPort: 8008,
        }
      ],

      all: [
        $.service(serverParams, env),
        $.deploymentSpec(serverParams, env,
                        [
                          $.containerSpec(serverParams, env=containerEnv,
                                          volumeMounts=containerVolumeMounts,
                                          ports=containerPorts)
                        ],
                        volumes=volumes),
      ],
    }.all,
  }
}
