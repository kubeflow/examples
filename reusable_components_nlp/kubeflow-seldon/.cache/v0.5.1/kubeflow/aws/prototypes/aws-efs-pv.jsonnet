// @apiVersion 0.1
// @name io.ksonnet.pkg.aws-efs-pv
// @description Creates PV and PVC based on AWS EFS
// @shortDescription Creates PV and PVC based on AWS EFS
// @param name string Name for the component
// @optionalParam storageCapacity string 100Gi Storage Capacity
// @optionalParam storageClassName string efs-default Storage Capacity
// @param efsId string AWS EFS File System ID
// @optionalParam image string gcr.io/kubeflow-images-public/ubuntu:18.04 The docker image to use

local aws_efs_pv = import "kubeflow/aws/aws-efs-pv.libsonnet";
local instance = aws_efs_pv.new(env, params);
instance.list(instance.all)
