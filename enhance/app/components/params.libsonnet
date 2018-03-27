{
  global: {
    // User-defined global parameters; accessible to all component and environments, Ex:
    // replicas: 4,
  },
  components: {
    // Component-level parameters, defined initially from 'ks prototype use ...'
    // Each object below should correspond to a component in the components/ directory
    "tensorboard":{
      log_dir: "/mnt/nfs-1/train_dirs/allen_brain_img2img/img2img_transformer-img2img_transformer_tiny/0315-1728-d68d",
      name: "enhance-0317-0208-cd7b",
      namespace: "kubeflow",
      nfs_claim: "nfs-1",
    },
    "train": {
      app_name: "enhance",
      data_dir: "",
      data_root: "/mnt/nfs-1/datasets/alleninst/mouse",
      decode_hparams: "",
      decode_source_file: "none",
      decode_target_file: "",
      eval_steps: 1,
      hparam_id: "img2img_transformer_tiny",
      hparams_set: "img2img_transformer_tiny",
      job_name: "allen-brain-img2img-0317-0257-bc43",
      model: "img2img_transformer",
      namespace: "kubeflow",
      nfs_claim: "nfs-1",
      num_cpu: 1,
      problem: "allen_brain_img2img",
      replicas: 1,
      "t2t_command": "t2t-trainer",
      "t2t_usr_dir": "/mnt/nfs-1/train_dirs/allen_brain_img2img/img2img_transformer-img2img_transformer_tiny/0317-0257-bc43/workspace/enhance/py",
      tmp_dir: "",
      train_dir: "/mnt/nfs-1/train_dirs/allen_brain_img2img/img2img_transformer-img2img_transformer_tiny/0317-0257-bc43",
      train_steps: 100,
    },
   "job": {
      backoffLimit: 4,
      image: "ubuntu",
      name: "test",
      namespace: "kubeflow",
      restartPolicy: "Never",
      command: ["ls"]
    },
  },
}
