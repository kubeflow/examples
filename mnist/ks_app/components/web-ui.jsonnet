local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["web-ui"];
[
  {
    "apiVersion": "v1",
    "kind": "Service",
    "metadata": {
      "name": params.name,
      "namespace": env.namespace,
      annotations: {
        "getambassador.io/config":
          std.join("\n", [
            "---",
            "apiVersion: ambassador/v0",
            "kind:  Mapping",
            "name: " + params.name + "_mapping",
            "prefix: /" + env.namespace + "/mnist/",
            "rewrite: /",
            "service: " + params.name + "." + env.namespace,
          ]),
      },  //annotations
    },
    "spec": {
      "ports": [
        {
          "port": params.servicePort,
          "targetPort": params.containerPort
        }
      ],
      "selector": {
        "app": params.name
      },
      "type": params.type
    }
  },
  {
    "apiVersion": "apps/v1beta2",
    "kind": "Deployment",
    "metadata": {
      "name": params.name,
      "namespace": env.namespace,
    },
    "spec": {
      "replicas": params.replicas,
      "selector": {
        "matchLabels": {
          "app": params.name
        },
      },
      "template": {
        "metadata": {
          "labels": {
            "app": params.name
          }
        },
        "spec": {
          "containers": [
            {
              "image": params.image,
              "name": params.name,
              "ports": [
                {
                  "containerPort": params.containerPort
                }
              ]
            }
          ]
        }
      }
    }
  }
]
