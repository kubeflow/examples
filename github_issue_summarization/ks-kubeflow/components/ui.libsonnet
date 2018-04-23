{
  parts(params, env):: [
    {
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
        type: "ClusterIP",
      },
    },
    {
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
                image: "gcr.io/kubeflow-images-staging/issue-summarization-ui:latest",
		env: [
		{
		  name: "GITHUB_TOKEN",
		  value: params.github_token,
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
    },
  ],
}
