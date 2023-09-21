# Qiskit_Pipeline
The goal of node-red-quantum-kube is to integrate Kubeflow/Kubebeters with Node-RED, while utilizing Node-RED's low-code modules, while using Kubeflow resources (such as Kubeflow pipeline, Kserve) to enhance its artificial intelligence/machine learning ability.

## References
https://github.com/kubeflow/pipelines/tree/1.8.21/backend/api/python_http_client

https://github.com/namgk/node-red-contrib-pythonshell/tree/master

## Instructions for use
### prepare in advance

Since this project is focused on integrating Node-RED with Kubeflow, it requires a running Kubeflow instance configured on a publicly available network.
(If you need to configure your own Kubeflow instance, you can refer to our [mulitkf](https://github.com/footprintai/multikf) project to configure an instance for development.)

### Build container image

You can go to the [examples](./examples/README.md) folder and run `./build.sh` to build the image locally, or just run `./run.sh` and it will read from our public Download the base image from the repository.

### Execution example

We organize some examples in the [examples](./examples/README.md) folder and pass sensitive information through environment variables. Please refer to the following examples to start individual examples:
```
# Enter the folder
cd kubeflow-Node-RED

cd examples && \
KUBEFLOW_HOST=<your-kubeflow-instance-endpoint> \
KUBEFLOW_USERNAME=<your-username-account> \
KUBEFLOW_PASSWORD=<your-password> \
./run.sh <example-index>
```
> **Note:** Here <example-index> please use 1.connect-kubeflow


## Kubeflow part:
### YAML file for custom process
Please refer to [Kubeflow Implementation: Add Random Forest Algorithm](https://hackmd.io/@Nhi7So-lTz2m5R6pHyCLcA/Sk1eZFTbh)

### Take modifying <span>qnn.py<span> as an example

Modify the path to use your own YAML file
> **Note:** Line 66: uploadfile='pipelines/qnnPipeline.yaml'

> **Note:** Lines 122 to 129 use a JSON parser to filter the different output of get_run()

```python=
from __future__ import print_function

import time
import kfp_server_api
import os
import requests
import string
import random
import json
from kfp_server_api.rest import ApiException
from pprint import pprint
from kfp_login import get_istio_auth_session
from kfp_namespace import retrieve_namespaces

host = os.getenv("KUBEFLOW_HOST")
username = os.getenv("KUBEFLOW_USERNAME")
password = os.getenv("KUBEFLOW_PASSWORD")

auth_session = get_istio_auth_session(
        url=host,
        username=username,
        password=password
    )

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: Bearer
configuration = kfp_server_api.Configuration(
    host = os.path.join(host, "pipeline"),
)
configuration.debug = True

namespaces = retrieve_namespaces(host, auth_session)
#print("available namespace: {}".format(namespaces))

def random_suffix() -> string:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

# Enter a context with an instance of the API client
with kfp_server_api.ApiClient(configuration, cookie=auth_session["session_cookie"]) as api_client:
    # Create an instance of the  Experiment API class
    experiment_api_instance = kfp_server_api.ExperimentServiceApi(api_client)
    name="experiment-" + random_suffix()
    description="This is a experiment for qnn."
    resource_reference_key_id = namespaces[0]
    resource_references=[kfp_server_api.models.ApiResourceReference(
        key=kfp_server_api.models.ApiResourceKey(
            type=kfp_server_api.models.ApiResourceType.NAMESPACE,
            id=resource_reference_key_id
        ),
        relationship=kfp_server_api.models.ApiRelationship.OWNER
    )]
    body = kfp_server_api.ApiExperiment(name=name, description=description, resource_references=resource_references) # ApiExperiment | The experiment to be created.
    try:
        # Creates a new experiment.
        experiment_api_response = experiment_api_instance.create_experiment(body)
        experiment_id = experiment_api_response.id # str | The ID of the run to be retrieved.
    except ApiException as e:
        print("Exception when calling ExperimentServiceApi->create_experiment: %s\n" % e)
    
    # Create an instance of the pipeline API class
    api_instance = kfp_server_api.PipelineUploadServiceApi(api_client) 
    uploadfile='pipelines/qnnPipeline.yaml'
    name='pipeline-' + random_suffix()
    description="This is a qnn pipeline."
    try:
        pipeline_api_response = api_instance.upload_pipeline(uploadfile, name=name, description=description)
        pipeline_id = pipeline_api_response.id # str | The ID of the run to be retrieved.
    except ApiException as e:
        print("Exception when calling PipelineUploadServiceApi->upload_pipeline: %s\n" % e)

    # Create an instance of the run API class
    run_api_instance = kfp_server_api.RunServiceApi(api_client)
    display_name = 'run_qnn_pipeline' + random_suffix()
    description = "This is a qnn pipeline."
    pipeline_spec = kfp_server_api.ApiPipelineSpec(pipeline_id=pipeline_id)
    resource_reference_key_id = namespaces[0]
    resource_references=[kfp_server_api.models.ApiResourceReference(
    key=kfp_server_api.models.ApiResourceKey(id=experiment_id, type=kfp_server_api.models.ApiResourceType.EXPERIMENT),
    relationship=kfp_server_api.models.ApiRelationship.OWNER )]
    body = kfp_server_api.ApiRun(name=display_name, description=description, pipeline_spec=pipeline_spec, resource_references=resource_references) # ApiRun | 
    try:
        # Creates a new run.
        run_api_response = run_api_instance.create_run(body)
        run_id = run_api_response.run.id # str | The ID of the run to be retrieved.
    except ApiException as e:
        print("Exception when calling RunServiceApi->create_run: %s\n" % e)

    Completed_flag = False
    polling_interval = 10  # Time in seconds between polls

    while not Completed_flag:
        try:
            time.sleep(1)
            # Finds a specific run by ID.
            api_instance = run_api_instance.get_run(run_id)
            output = api_instance.pipeline_runtime.workflow_manifest
            output = json.loads(output)

            try:
                nodes = output['status']['nodes']
                conditions = output['status']['conditions'] # Comfirm completion.
                
            except KeyError:
                nodes = {}
                conditions = []

            output_value = None
            Completed_flag = conditions[1]['status'] if len(conditions) > 1 else False

        except ApiException as e:
            print("Exception when calling RunServiceApi->get_run: %s\n" % e)
            break

        if not Completed_flag:
            print("Pipeline is still running. Waiting...")
            time.sleep(polling_interval-1)

        for node_id, node in nodes.items():
                if 'inputs' in node and 'parameters' in node['inputs']:
                    for parameter in node['inputs']['parameters']:
                        if parameter['name'] == 'qnn-Accuracy':
                            output_value = parameter['value']
                            
    if output_value is not None:
        print(output_value)
    else:
        print("Parameter not found.")
        print(nodes)
```
### Test python file
```
# Make sure dependencies are installed
pip install kfp
python <python-file>
```
## Node-red part: **PyShell node that encapsulates Node-RED**

**A node mainly consists of two files**

* **Javascript file (.js)**
Define the function of the node
* **HTML file (.html)**
Define node properties, windows and help messages in the Node-RED editor
    
**When finally packaged as an npm module, package.json needs to be included**


### **package.json**
A standard file describing the contents of a Node.js module

A standard package.json can be generated using the npm init command. The command asks a series of questions to find reasonable defaults. When asked for a module name, enter <default value> for the example name node-red-contrib-<self_defined>.

After the package.json is created, you need to manually add the node-red attribute.
*p.s. Need to change the location of the sample files *
    


```json=
{
  "name": "node-red-contrib-pythonshell-custom",
  ...
  "node-red": {
    "nodes": {
      "qnn": "qnn.js"
      "<self_defined>":"<self_defined.js>"
    }
  },
  ...
}

```
### **HTML**
```javascript=
<script type="text/javascript">
# Replace the node name displayed/registered in the palette
  RED.nodes.registerType('qnn',{
    category: 'input',
    defaults: {
      name: {required: false},
# Replace the .py path to be used
      pyfile: {value: "/data/1.connect-kubeflow/py/qnn.py"},
      virtualenv: {required: false},
      continuous: {required: false},
      stdInData: {required: false},
      python3: {required: false}
    },
```
### **Javascript(main function)**
1. Open the qnn0.js file
```javascript=
function PythonshellInNode(config) {
  if (!config.pyfile){
    throw 'pyfile not present';
  }
  this.pythonExec = config.python3 ? "python3" : "python";
  # Replace the path or change the following path to config.pyfile
  this.pyfile = '/data/1.connect-kubeflow/py/qnn.py';
  this.virtualenv = config.virtualenv;
```
2. Open the qnn.js file 
```javascript=
var util = require("util");
var httpclient;
#change the path/file name of the module file
var PythonshellNode = require('./qnn0');
      
# To change the name to be registered, it must be consistent with the change of .html
RED.nodes.registerType("qnn", PythonshellInNode);
```
### Test Results

1. Start Node-RED, open the editor, and you should be able to find a node named qnn in the function block.
2. The node takes input, processes it using the specified python file, and returns the result as output. You can use other nodes to pass the input to the qnn node and connect the output to other nodes.
3. Finally, start Kubeflow and open the editor. You should be able to find the pipeline named This is a only_qnn pipline in the Description in the pipeline block. Click on the pipeline and press Show-results to see the results.


## Video presentation

[Qnn](https://youtu.be/cEZkK4TbK0Y)



