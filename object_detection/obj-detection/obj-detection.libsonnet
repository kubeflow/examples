{
    get_data_job(namespace, name, pvc, url, mountPath):: {
      apiVersion: "batch/v1",
      kind: "Job",
      metadata: {
        name: name,
        namespace: namespace,
      },
      spec: {
        template: {
          spec: {
            containers: [{
              name: "get-data",
              image: "inutano/wget",
              imagePullPolicy: "IfNotPresent",
              command: ["wget",  url, "-P", mountPath],
              volumeMounts: [{
                  mountPath: mountPath,
                  name: "pets-data",
              },],
              },],
            volumes: [{
                name: "pets-data",
                persistentVolumeClaim: {
                  claimName: pvc,
                },
            },],
            restartPolicy: "Never",
          },
        },
        backoffLimit: 4,
      },
    },

    decompress_job(namespace, name, pvc, pathToFile, mountPath)::{
      apiVersion: "batch/v1",
      kind: "Job",
      metadata: {
        name: name,
        namespace: namespace,
      },
      spec: {
        template: {
          spec: {
            containers: [{
              name: "decompress-data",
              image: "ubuntu:16.04",
              imagePullPolicy: "IfNotPresent",
              command: ["tar", "--no-same-owner", "-xzvf",  pathToFile, "-C", "mountPath"],
              volumeMounts: [{
                  mountPath: mountPath,
                  name: "pets-data",
              },],
              },],
            volumes: [{
                name: "pets-data",
                persistentVolumeClaim: {
                  claimName: pvc,
                },
            },],
            restartPolicy: "Never",
          },
        },
        backoffLimit: 4,
      },
    },

    pvc(namespace, name, storage, accessMode)::{
      apiVersion: "v1",
      kind: "PersistentVolumeClaim",
      metadata:{
        name: name,
        namespace: namespace,
      },
      spec:{
        accessModes: [accessMode],
        volumeMode: "Block",
        resources: {
          requests: {
            storage: storage,
          },
        },
      },
    },

    export_tf_graph_job(namespace, name, image, command, args, pvc, mountPath)::{
      apiVersion: "batch/v1",
      kind: "Job",
      metadata: {
        name: name,
        namespace: namespace,
      },
      spec: {
        template: {
          spec: {
            containers: [{
              name: "export-graph",
              image: image,
              imagePullPolicy: "IfNotPresent",
              command: command,
              args: args,
              volumeMounts: [{
                  mountPath: mountPath,
                  name: "pets-data",
              },],
              },],
            volumes: [{
                name: "pets-data",
                persistentVolumeClaim: {
                  claimName: pvc,
                },
            },],
            restartPolicy: "Never",
          },
        },
        backoffLimit: 4,
      },
    },
}