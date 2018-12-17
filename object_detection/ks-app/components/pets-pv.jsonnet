local env = std.extVar("__ksonnet/environments");
local params = std.extVar("__ksonnet/params").components["pets-pv"];
local pvcparams = std.extVar("__ksonnet/params").components["pets-pvc"];

local k = import "k.libsonnet";

local pv = {
  apiVersion: "v1",
  kind: "PersistentVolume",
  metadata:{
    name: params.name,
    namespace: env.namespace,
  },
  spec:{
    accessModes: [pvcparams.accessMode],
    capacity: {
        storage: pvcparams.storage,
    },
    nfs: {
      path: params.nfsDir,
      server: params.nfsServer,
    },
  },
};

std.prune(k.core.v1.list.new([pv],))
