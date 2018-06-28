{
  all(params, env):: [
    $.parts(params, env).service,
    $.parts(params, env).deployment,
  ],

  parts(params, env):: {
    // Define some defaults.
    local updatedParams = {
      serviceType: "ClusterIP",
      image: "gcr.io/kubeflow-images-public/issue-summarization-ui:latest",
      modelUrl: "http://issue-summarization.kubeflow.svc.cluster.local:8000/api/v0.1/predictions",
    } + params,

    service:: {
      apiVersion: "v1",
      kind: "Service",
      metadata: {
        name: "issue-summarization-ui",
        namespace: env.namespace,
        annotations: {
          "getambassador.io/config": "---\napiVersion: ambassador/v0\nkind:  Mapping\nname:  issue_summarization_ui\nprefix: /issue-summarization/\nrewrite: /\nservice: issue-summarization-ui:80\n",
        },
      },
      spec: {
        ports: [
          {
            port: 80,
            targetPort: 80,
          },
        ],
        selector: {
          app: "issue-summarization-ui",
        },
        type: updatedParams.serviceType,
      },
    },

    deployment:: {
      apiVersion: "apps/v1beta1",
      kind: "Deployment",
      metadata: {
        name: "issue-summarization-ui",
        namespace: env.namespace,
      },
      spec: {
        replicas: 1,
        template: {
          metadata: {
            labels: {
              app: "issue-summarization-ui",
            },
          },
          spec: {
            containers: [
              {
                args: [
                  "app.py",
                  "--model_url",
                  updatedParams.modelUrl,
                ],
                command: [
                  "python",
                ],
                image: updatedParams.image,
		env: [
		{
		  name: "GITHUB_TOKEN",
		  value: updatedParams.githubToken,
		}
		],
                name: "issue-summarization-ui",
                ports: [
                  {
                    containerPort: 80,
                  },
                ],
              },
            ],
          },
        },
      },
    }, // deployment
  }, // parts
}
