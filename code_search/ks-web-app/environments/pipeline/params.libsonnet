local params = std.extVar('__ksonnet/params');
local globals = import 'globals.libsonnet';
local envParams = params + {
  components+: {
    "search-index-server"+: {
      indexFile: 'gs://code-search-demo/pipeline/recurrentbvqw5-5-2446024910/code-embeddings-index/embeddings.index',
      lookupFile: 'gs://code-search-demo/pipeline/recurrentbvqw5-5-2446024910/code-embeddings-index/embedding-to-info.csv',
    },
  },
};

{
  components: {
    [x]: envParams.components[x] + globals
    for x in std.objectFields(envParams.components)
  },
}