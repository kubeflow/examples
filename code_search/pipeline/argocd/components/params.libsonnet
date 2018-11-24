{
  global: {},
  components: {
    "search-index-server": {
      name: "search-index-server",
      problem: "kf_github_function_docstring",
      dataDir: "gs://example/prefix/data",
      lookupFile: "gs://example/prefix/data/code_search_index.csv",
      indexFile: "gs://example/prefix/data/code_search_index.nmslib",
      servingUrl: "http://t2t-code-search.kubeflow:9001/v1/models/t2t-code-search:predict",
    },
    nmslib: {
      replicas: 1,
      image: "gcr.io/kubeflow-dev/code-search-ui:v20180817-0d4a60d",
      problem: "null",
      dataDir: "null",
      lookupFile: "null",
      indexFile: "null",
      servingUrl: "null",
    },    
  },
}
