// Run a job to download the data to a persistent volume.
//
local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["data-pvc"];
local k = import "k.libsonnet";


local script = importstr "download_data.sh";

local scriptConfigMap = {
  apiVersion: "v1",
  kind: "ConfigMap",
  metadata: {
    name: "downloader",
    namespace: env.namespace,
  },

  data: {
    "download_data.sh": script,
  },
};

local downLoader = {
  apiVersion: "batch/v1",
  kind: "Job",
  metadata: {
    name: "download-data",
    namespace: env.namespace,
  },
  spec: {
    backoffLimit: 4,
    template: {
      spec: {
        containers: [
          {
            command: [
              "/bin/ash",
              "/scripts/download_data.sh",
            ],
            image: "busybox",
            name: "downloader",
            volumeMounts: [
              {
                name: "script",
                mountPath: "/scripts",
              },
              {
                name: "data",
                mountPath: "/data",
              },
            ],
          },
        ],
        restartPolicy: "Never",
        volumes: [
          {
            name: "script",
            configMap: {
              name: "downloader",
            },
          },
          {
            name: "data",
            persistentVolumeClaim: {
              claimName: "data-pvc",
            },
          },
        ],
      },
    },
  },
};

std.prune(k.core.v1.list.new([downLoader, scriptConfigMap]))
