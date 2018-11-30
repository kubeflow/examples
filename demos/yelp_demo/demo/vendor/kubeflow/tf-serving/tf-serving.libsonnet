{
  // Parameters are intended to be late bound.
  params:: {
    name: null,
    numGpus: 0,
    labels: {
      app: $.params.name,
    },
    modelName: $.params.name,
    modelPath: null,

    deployHttpProxy: true,
    defaultHttpProxyImage: "gcr.io/kubeflow-images-staging/tf-model-server-http-proxy:v20180327-995786ec",
    httpProxyImage: "",
    httpProxyImageToUse: if $.params.httpProxyImage == "" then
      $.params.defaultHttpProxyImage
    else
      $.params.httpProxyImage,

    serviceType: "ClusterIP",

    // If users want to override the image then can override defaultCpuImage and/or defaultGpuImage
    // in which case the image used will still depend on whether GPUs are used or not.
    // Users can also override modelServerImage in which case the user supplied value will always be used
    // regardless of numGpus.
    defaultCpuImage: "gcr.io/kubeflow-images-staging/tf-model-server-cpu:v20180327-995786ec",
    defaultGpuImage: "gcr.io/kubeflow-images-staging/tf-model-server-gpu:v20180327-995786ec",
    modelServerImage: if $.params.numGpus == 0 then
      $.params.defaultCpuImage
    else
      $.params.defaultGpuImage,


    // Whether or not to enable s3 parameters
    s3Enable:: false,

    // Which cloud to use
    cloud:: null,
  },

  // Parametes specific to GCP.
  gcpParams:: {
    gcpCredentialSecretName: "",
  } + $.params,

  // Parameters that control S3 access
  // params overrides s3params because params can be overwritten by the user to override the defaults.
  s3params:: {
    //  Name of the k8s secrets containing S3 credentials
    s3SecretName: "",
    // Name of the key in the k8s secret containing AWS_ACCESS_KEY_ID.
    s3SecretAccesskeyidKeyName: "",

    // Name of the key in the k8s secret containing AWS_SECRET_ACCESS_KEY.
    s3SecretSecretaccesskeyKeyName: "",

    // S3 region
    s3AwsRegion: "us-west-1",

    // TODO(jlewi): We should use util.toBool to automatically conver to actual boolean values.
    // The use of strings is left over from when they were prototype parameters which only supports string type.

    // true Whether or not to use https for S3 connections
    s3UseHttps: "true",

    // Whether or not to verify https certificates for S3 connections
    s3VerifySsl: "true",

    // URL for your s3-compatible endpoint.
    s3Endpoint: "http://s3.us-west-1.amazonaws.com,",
  } + $.params,


  components:: {

    all::
      // TODO(jlewi): It would be better to structure s3 as a mixin.
      // As an example it would be great to allow S3 and GCS parameters
      // to be enabled simultaneously. This should be doable because
      // each entails adding a set of environment variables and volumes
      // to the containers. These volumes/environment variables shouldn't
      // overlap so there's no reason we shouldn't be able to just add
      // both modifications to the base container.
      // I think we want to restructure things as mixins so they can just
      // be added.
      if $.params.s3Enable then
        [
          $.s3parts.tfService,
          $.s3parts.tfDeployment,
        ]
      else if $.params.cloud == "gcp" then
        [
          $.gcpParts.tfService,
          $.gcpParts.tfDeployment,
        ]
      else
        [
          $.parts.tfService,
          $.parts.tfDeployment,
        ],
  }.all,

  parts:: {
    // We define the containers one level beneath parts because combined with jsonnet late binding
    // this makes it easy for users to override specific bits of the container.
    tfServingContainerBase:: {
      name: $.params.name,
      image: $.params.modelServerImage,
      imagePullPolicy: "IfNotPresent",
      args: [
        "/usr/bin/tensorflow_model_server",
        "--port=9000",
        "--model_name=" + $.params.modelName,
        "--model_base_path=" + $.params.modelPath,
      ],
      ports: [
        {
          containerPort: 9000,
        },
      ],
      // TODO(jlewi): We should add readiness and liveness probes. I think the blocker is that
      // model-server doesn't have something we can use out of the box.
      resources: {
        requests: {
          memory: "1Gi",
          cpu: "1",
        },
        limits: {
          memory: "4Gi",
          cpu: "4",
        },
      },
    },  // tfServingContainer

    tfServingContainer+: $.parts.tfServingContainerBase +
                         if $.params.numGpus > 0 then
                           {
                             resources+: {
                               limits+: {
                                 "nvidia.com/gpu": $.params.numGpus,
                               },
                             },
                           }
                         else {},


    httpProxyContainer:: {
      name: $.params.name + "-http-proxy",
      image: $.params.httpProxyImageToUse,
      imagePullPolicy: "IfNotPresent",
      command: [
        "python",
        "/usr/src/app/server.py",
        "--port=8000",
        "--rpc_port=9000",
        "--rpc_timeout=10.0",
      ],
      env: [],
      ports: [
        {
          containerPort: 8000,
        },
      ],
      resources: {
        requests: {
          memory: "1Gi",
          cpu: "1",
        },
        limits: {
          memory: "4Gi",
          cpu: "4",
        },
      },
    },  // httpProxyContainer


    tfDeployment: {
      apiVersion: "extensions/v1beta1",
      kind: "Deployment",
      metadata: {
        name: $.params.name,
        namespace: $.params.namespace,
        labels: $.params.labels,
      },
      spec: {
        template: {
          metadata: {
            labels: $.params.labels,
          },
          spec: {
            containers: [
              $.parts.tfServingContainer,
              if $.params.deployHttpProxy then
                $.parts.httpProxyContainer,
            ],
            // See:  https://github.com/kubeflow/kubeflow/tree/master/components/k8s-model-server#set-the-user-optional
            // The is user and group should be defined in the Docker image.
            // Per best practices we don't run as the root user.
            securityContext: {
              runAsUser: 1000,
              fsGroup: 1000,
            },
          },
        },
      },
    },  // tfDeployment

    tfService: {
      apiVersion: "v1",
      kind: "Service",
      metadata: {
        labels: $.params.labels,
        name: $.params.name,
        namespace: $.params.namespace,
        annotations: {
          "getambassador.io/config":
            std.join("\n", [
              "---",
              "apiVersion: ambassador/v0",
              "kind:  Mapping",
              "name: tfserving-mapping-" + $.params.name + "-get",
              "prefix: /models/" + $.params.name + "/",
              "rewrite: /",
              "method: GET",
              "service: " + $.params.name + "." + $.params.namespace + ":8000",
              "---",
              "apiVersion: ambassador/v0",
              "kind:  Mapping",
              "name: tfserving-mapping-" + $.params.name + "-post",
              "prefix: /models/" + $.params.name + "/",
              "rewrite: /model/" + $.params.name + ":predict",
              "method: POST",
              "service: " + $.params.name + "." + $.params.namespace + ":8000",
            ]),
        },  //annotations
      },
      spec: {
        ports: [
          {
            name: "tf-serving",
            port: 9000,
            targetPort: 9000,
          },
          {
            name: "tf-serving-proxy",
            port: 8000,
            targetPort: 8000,
          },
        ],
        selector: $.params.labels,
        type: $.params.serviceType,
      },
    },  // tfService

  },  // parts

  // Parts specific to S3
  s3parts:: $.parts {
    s3Env:: [
      { name: "AWS_ACCESS_KEY_ID", valueFrom: { secretKeyRef: { name: $.s3params.s3SecretName, key: $.s3params.s3SecretAccesskeyidKeyName } } },
      { name: "AWS_SECRET_ACCESS_KEY", valueFrom: { secretKeyRef: { name: $.s3params.s3SecretName, key: $.s3params.s3SecretSecretaccesskeyKeyName } } },
      { name: "AWS_REGION", value: $.s3params.s3AwsRegion },
      { name: "S3_REGION", value: $.s3params.s3AwsRegion },
      { name: "S3_USE_HTTPS", value: $.s3params.s3UseHttps },
      { name: "S3_VERIFY_SSL", value: $.s3params.s3VerifySsl },
      { name: "S3_ENDPOINT", value: $.s3params.s3Endpoint },
    ],

    tfServingContainer: $.parts.tfServingContainer {
      env+: $.s3parts.s3Env,
    },

    tfDeployment: $.parts.tfDeployment {
      spec: +{
        template: +{

          spec: +{
            containers: [
              $.s3parts.tfServingContainer,
              if $.params.httpProxyImage != 0 then
                $.parts.httpProxyContainer,
            ],
          },
        },
      },
    },  // tfDeployment
  },  // s3parts

  // Parts specific to GCP
  gcpParts:: $.parts {
    gcpEnv:: [
      if $.gcpParams.gcpCredentialSecretName != "" then
        { name: "GOOGLE_APPLICATION_CREDENTIALS", value: "/secret/gcp-credentials/key.json" },
    ],

    tfServingContainer: $.parts.tfServingContainer {
      env+: $.gcpParts.gcpEnv,
      volumeMounts+: [
        if $.gcpParams.gcpCredentialSecretName != "" then
          {
            name: "gcp-credentials",
            mountPath: "/secret/gcp-credentials",
          },
      ],
    },

    tfDeployment: $.parts.tfDeployment {
      spec+: {
        template+: {

          spec+: {
            containers: [
              $.gcpParts.tfServingContainer,
              if $.params.httpProxyImage != 0 then
                $.parts.httpProxyContainer,
            ],

            volumes: [
              if $.gcpParams.gcpCredentialSecretName != "" then
                {
                  name: "gcp-credentials",
                  secret: {
                    secretName: $.gcpParams.gcpCredentialSecretName,
                  },
                },
            ],
          },
        },
      },
    },  // tfDeployment
  },  // gcpParts
}
