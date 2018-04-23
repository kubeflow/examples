local params = import "../../components/params.libsonnet";
params + {
  components +: {
    // Insert component parameter overrides here. Ex:
    // guestbook +: {
    //   name: "guestbook-dev",
    //   replicas: params.global.replicas,
    // },
    "kubeflow-core" +: {
      cloud: "gke",
    },
    ui +: {
      github_token: "109e464a0ced54a1fe1987a0d3af8f0a3b2064bc",
    },
  },
}
