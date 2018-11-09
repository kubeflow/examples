local params = std.extVar('__ksonnet/params');
local globals = import 'globals.libsonnet';
local envParams = params + {
  components+: {
    "t2t-code-search"+: {      
    },
    "t2t-code-search-datagen"+: {            
      githubTable: '',
    },
    "submit-preprocess-job"+: {      
      githubTable: '',
    },
  },
};

{
  components: {
    [x]: envParams.components[x] + globals
    for x in std.objectFields(envParams.components)
  },
}