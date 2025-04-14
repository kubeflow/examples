The goal of node-red-quantum-kube is to integrate quantum machine learning from IBM qiskit with both the Kubeflow/Kubebeters and Node-RED repo.s.  Node-RED features low-code GUI modules for IOT applications.  By combining both qiskit and Kubeflow resources (such as Kubeflow pipeline, Kserve) under the hood of Node-red, users are able to expedite the development and deployment speed of quantum artificial intelligence/machine learning ability of real world applications. 
The structure of this repo. 


# Table of content
[TOC]
## reference
https://github.com/namgk/node-red-contrib-pythonshell/tree/master

https://qiskit.org/ecosystem/machine-learning/tutorials/05_torch_connector.html

## Usage explanation
### preparation

Since this project focuses on the integration of Node-RED and qiskit with kubeflow resources such as pipeline and kserve, it requires a running Kubeflow instance and configuration on a publicly available network.
(If you need to configure your own Kubeflow instance with your own qiskit app., you can refer to our [mulitkf](https://github.com/footprintai/multikf) project to configure an instance for development.)

### container image build
You can build the image locally by going to the [examples](./examples/README.md) folder and running `./build.sh`, or just run `./run.sh` and it will download the base image from our public Download site.
### execute example

We have compiled some examples in the [examples](./examples/README.md) folder and pass sensitive information through environment variables. Please refer to the following examples to start individual examples:
```
# enter directory
cd kubeflow-Node-RED

cd examples && \
KUBEFLOW_HOST=<your-kubeflow-instance-endpoint> \
KUBEFLOW_USERNAME=<your-username-account> \
KUBEFLOW_PASSWORD=<your-password> \
./run.sh <example-index>
```
#Note:** Please use 1.connect-kubeflow for <example-index> here
## Node-red part: **encapsulate Node-RED PyShell node**

**one Node-red node consists of two files:Javascript and HTML**

* **Javascript file (.js) define node functionality**
* **HTML file (.html) define nodal appearance and message properties **
    
**Finally we use package.json to form npm modules**

### **package.json**
node-red-contrib-<self_defined>。

A standard file describing the contents of a Node.js module
A standard package.json can be generated using the npm init command. The command asks a series of questions to find reasonable default values. When asked for a module name, enter <default value> as the example name node-red-contrib-<self_defined>.

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
1. open qnn0.js file
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
2.open qnn.js file
```javascript=
var util = require("util");
var httpclient;
#change the path/file name of the module file
var PythonshellNode = require('./qnn0');
      
# To change the name to be registered, it must be consistent with the change of .html
RED.nodes.registerType("qnn", PythonshellInNode);
```
### test results

Start Node-RED, open the editor, and you should be able to find the node named qnn in the function block.

This node accepts input, processes it using the specified python archive, and returns the result as output. You can use other nodes to pass input to the qnn node and connect output to other nodes.

## Demo video

[Qnn](https://youtu.be/cEZkK4TbK0Y)


