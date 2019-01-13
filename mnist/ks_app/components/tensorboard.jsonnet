// TODO: Generalize to use S3. We can follow the pattern of training that
// takes parameters to specify environment variables and secret which can be customized
// for GCS, S3 as needed.
local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components.tensorboard;

local k = import "k.libsonnet";

local name = params.name;
local namespace = env.namespace;
local service = {
  apiVersion: "v1",
  kind: "Service",
  metadata: {
    name: name + "-tb",
    namespace: env.namespace,
    annotations: {
      "getambassador.io/config":
        std.join("\n", [
          "---",
          "apiVersion: ambassador/v0",
          "kind:  Mapping",
          "name: " + name + "_mapping",
          "prefix: /" + env.namespace + "/tensorboard/mnist",
          "rewrite: /",
          "service: " + name + "-tb." + namespace,
          "---",
          "apiVersion: ambassador/v0",
          "kind:  Mapping",
          "name: " + name + "_mapping_data",
          "prefix: /" + env.namespace + "/tensorboard/mnist/data/",
          "rewrite: /data/",
          "service: " + name + "-tb." + namespace,
        ]),
    },  //annotations
  },
  spec: {
    ports: [
      {
        name: "http",
        port: 80,
        targetPort: 80,
      },
    ],
    selector: {
      app: "tensorboard",
      "tb-job": name,
    },
  },
};

local deployment = {
  apiVersion: "apps/v1beta1",
  kind: "Deployment",
  metadata: {
    name: name + "-tb",
    namespace: env.namespace,
  },
  spec: {
    replicas: 1,
    template: {
      metadata: {
        labels: {
          app: "tensorboard",
          "tb-job": name,
        },
        name: name,
        namespace: namespace,
      },
      spec: {
        containers: [
          {
            command: [
              "/usr/local/bin/tensorboard",
              "--logdir=" + params.logDir,
              "--port=80",
            ],
            image: params.image,
            name: "tensorboard",
            ports: [
              {
                containerPort: 80,
              },
            ],
            env: [
              {
                name: "GOOGLE_APPLICATION_CREDENTIALS",
                value: "/secret/gcp-credentials/user-gcp-sa.json",
              },
            ],
            volumeMounts: [
              {
                mountPath: "/secret/gcp-credentials",
                name: "gcp-credentials",
              },
            ],
          },
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
};

std.prune(k.core.v1.list.new([service, deployment]))

