// Submit a Dataflow job to preprocess the github public dataset
local k = import "k.libsonnet";

local experiments = import "experiments.libsonnet";
local lib = import "submit-preprocess-job.libsonnet";
local env = std.extVar("__ksonnet/environments");
local baseParams = std.extVar("__ksonnet/params").components["submit-preprocess-job"];
local experimentName = baseParams.experiment;
local params = baseParams + experiments[experimentName] + {
  name: experimentName + "-preprocess",
};


std.prune(k.core.v1.list.new([lib.parts(params,env).job]))
