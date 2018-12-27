local env = std.extVar("__ksonnet/environments");
local overrides = std.extVar("__ksonnet/params").components.code_search;

local k = import "k.libsonnet";
local util = import "util.libsonnet";

// Define default params and then combine them with any overrides
local defaultParams = {
  // local nfsVolumeClaim: "kubeflow-testing",
  nfsVolumeClaim: "nfs-external",

  // The name to use for the volume to use to contain test data.
  dataVolume: "kubeflow-test-volume",

  // Default step image:
  stepImage: "gcr.io/kubeflow-ci/test-worker:v20181017-bfeaaf5-dirty-4adcd0",

  // Image to use for running tests related to training/exporting models
  trainImage: "gcr.io/kubeflow-examples/code-search:v20181204-ee47a49-dirty-f4045c"
};

local params = defaultParams + overrides;

local prowEnv = util.parseEnv(params.prow_env);
local prowDict = util.listOfDictToMap(prowEnv);

local bucket = params.bucket;

// mountPath is the directory where the volume to store the test data
// should be mounted.
local mountPath = "/mnt/" + "test-data-volume";
// testDir is the root directory for all data for a particular test run.
local testDir = mountPath + "/" + params.name;
// outputDir is the directory to sync to GCS to contain the output for this job.
local outputDir = testDir + "/output";
local artifactsDir = outputDir + "/artifacts";

// Source directory where all repos should be checked out
local srcRootDir = testDir + "/src";

// The directory containing the kubeflow/kubeflow repo
local srcDir = srcRootDir + "/" + prowDict.REPO_OWNER + "/" + prowDict.REPO_NAME;


// Build template is a template for constructing Argo step templates.
//
// step_name: Name for the template
// command: List to pass as the container command.
//
// We customize the defaults for each step in the workflow by modifying
// buildTemplate.argoTemplate
local buildTemplate = {
  // name & command variables should be overwritten for every test.
  // Other variables can be changed per step as needed.
  // They are hidden because they shouldn't be included in the Argo template
  name: "",
  command:: "",
  image: params.stepImage,
  workingDir:: null,
  env_vars:: [],
  side_cars: [],


  activeDeadlineSeconds: 1800,  // Set 30 minute timeout for each template

  local template = self,

  // The directory within the kubeflow_testing submodule containing
  // py scripts to use.
  local kubeflowTestingPy = srcRootDir + "/kubeflow/testing/py",

  // Actual template for Argo
  argoTemplate: {
    name: template.name,
    container: {
      command: template.command,
      name: template.name,
      image: template.image,
      workingDir: template.workingDir,
      env: [
        {
          // Add the source directories to the python path.
          name: "PYTHONPATH",
          value: kubeflowTestingPy,
        },
        {
          name: "GOOGLE_APPLICATION_CREDENTIALS",
          value: "/secret/gcp-credentials/key.json",
        },
        {
          name: "GITHUB_TOKEN",
          valueFrom: {
            secretKeyRef: {
              name: "github-token",
              key: "github_token",
            },
          },
        },
      ] + prowEnv + template.env_vars,
      volumeMounts: [
        {
          name: params.dataVolume,
          mountPath: mountPath,
        },
        {
          name: "github-token",
          mountPath: "/secret/github-token",
        },
        {
          name: "gcp-credentials",
          mountPath: "/secret/gcp-credentials",
        },
      ],
    },
  },
};  // buildTemplate


// Create a list of dictionary.
// Each item is a dictionary describing one step in the graph.
local dagTemplates = [
  {
    template: buildTemplate {
      name: "checkout",
      command:
        ["/usr/local/bin/checkout.sh", srcRootDir],

      env_vars: [{
        name: "EXTRA_REPOS",
        value: "kubeflow/testing@HEAD",
      }],
    },
    dependencies: null,
  },  // checkout
  {
    // TODO(https://github.com/kubeflow/testing/issues/257): Create-pr-symlink
    // should be done by run_e2e_workflow.py
    template: buildTemplate {
      name: "create-pr-symlink",
      command: [
        "python",
        "-m",
        "kubeflow.testing.prow_artifacts",
        "--artifacts_dir=" + outputDir,
        "create_pr_symlink",
        "--bucket=" + params.bucket,
      ],
    },  // create-pr-symlink
    dependencies: ["checkout"],
  },  // create-pr-symlink
  {
    // Run the python test to train and export the model
    template: buildTemplate {
      name: "train-export-test",
      command: [
        "python3",
        "-m",
        "code_search.t2t.similarity_transformer_export_test",
      ],
      image: params.trainImage,
      workingDir: srcDir + "/code_search/src",      
    },
    dependencies: ["checkout"],
  },  // similarity_t2t_test
];

// Dag defines the tasks in the graph
local dag = {
  name: "e2e",
  // Construct tasks from the templates
  // we will give the steps the same name as the template
  dag: {
    tasks: util.toArgoTaskList(dagTemplates),
  },
};  // dag

// Define templates for the steps to be performed when the
// test exits
local exitTemplates =
  [
    {
      // Copy artifacts to GCS for gubernator.
      // TODO(https://github.com/kubeflow/testing/issues/257): Create-pr-symlink
      // should be done by run_e2e_workflow.py
      template: buildTemplate {
        name: "copy-artifacts",
        command: [
          "python",
          "-m",
          "kubeflow.testing.prow_artifacts",
          "--artifacts_dir=" + outputDir,
          "copy_artifacts",
          "--bucket=" + bucket,
        ],
      },  // copy-artifacts,

    },
    {
      // Delete the test directory in NFS.
      // TODO(https://github.com/kubeflow/testing/issues/256): Use an external process to do this.
      template:
        buildTemplate {
          name: "test-dir-delete",
          command: [           
            "rm",
            "-rf",
            testDir,
          ],

          argoTemplate+: {
        	  retryStrategy: {
        	  	limit: 3,
        	  },
          },
        },  // test-dir-delete
      dependencies: ["copy-artifacts"],
    },
  ];

// Create a DAG representing the set of steps to execute on exit
local exitDag = {
  name: "exit-handler",
  // Construct tasks from the templates
  // we will give the steps the same name as the template
  dag: {    
    tasks: util.toArgoTaskList(exitTemplates),    
  },
};

// A list of templates for the actual steps
local stepTemplates = std.map(function(i) i.template.argoTemplate
                              , dagTemplates) +
                      std.map(function(i) i.template.argoTemplate
                              , exitTemplates);

// Define the Argo Workflow.
local workflow = {
  apiVersion: "argoproj.io/v1alpha1",
  kind: "Workflow",
  metadata: {
    name: params.name,
    namespace: env.namespace,
    labels: {
      org: prowDict.REPO_OWNER,
      repo: prowDict.REPO_NAME,
      workflow: "code_search",
      [if std.objectHas(prowDict, "PULL_NUMBER") then "pr"]: prowDict.PULL_NUMBER,
    },
  },
  spec: {
    entrypoint: "e2e",
    volumes: [
      {
        name: "github-token",
        secret: {
          secretName: "github-token",
        },
      },
      {
        name: "gcp-credentials",
        secret: {
          secretName: "kubeflow-testing-credentials",
        },
      },
      {
        name: params.dataVolume,
        persistentVolumeClaim: {
          claimName: params.nfsVolumeClaim,
        },
      },
    ],  // volumes

    // onExit specifies the template that should always run when the workflow completes.
    onExit: "exit-handler",

    // The templates will be a combination of the templates
    // defining the dags executed by Argo as well as the templates
    // for the individual steps.
    templates: [dag, exitDag] + stepTemplates,  // templates
  },  // spec
};  // workflow

std.prune(k.core.v1.list.new([workflow]))