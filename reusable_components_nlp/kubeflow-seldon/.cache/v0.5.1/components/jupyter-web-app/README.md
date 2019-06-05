## Goals
- replace JupyterHub Spawner UI with a new Jupyter UI that natively manages Notebook CRs
- allow Users to create, connect to and delete Notebooks by specifying custom resources

## Design
The new Jupyter UI uses [Python Flask](http://flask.pocoo.org/) for the backend and HTML/jQuery/Material Design Lite for the frontend. A privileged `ServiceAccount` along with proper `RBAC` resources are associated with the Pod hosting the Flask server. In this manner, the `jupyter-web-app` Pod is allowed to manage Notebook CRs and PVCs in the `kubeflow` namespace.

Please note that as soon as the Profile Controller supports automatic creation of read/write ServiceAccounts for each `Profile`, the new Jupyter UI will be updated to use the respective JWTs and perform all K8s API requests via [K8s Impersonation](https://kubernetes.io/docs/reference/access-authn-authz/authentication/#user-impersonation). This will ultimately provide isolation of resources between Users and avoid any possible conflicts. For more information about User authentication and e2e workflow see the [Jupyter design doc](http://bit.ly/kf_jupyter_design_doc)


## User Interaction
As soon as the User points his/her browser to http://<KUBEFLOW_IP>/jupyter/ he/she will be directed to the new Jupyter UI. By default the UI will try to list the Notebooks in the namespace of its `ServiceAccount`, currently `kubeflow`, as mentioned above. If something goes wrong the UI will notify the user with an appropriate message containing info about the API call error.

From the Noteooks table he/she can either click the `+` button to create a new Notebook or perform `Delete`/`Connect` actions to an existing one. The UI only performs requests regarding the Notebook CRs to the K8s API server. The management of all child resources(`Service`, `Deployment`) is performed by the Notebook CR Controller.

By pressing the `+` button to create a Notebook the user is redirected to a form that allows him to configure the `PodTemplateSpec` params of the new Notebook. The User can specify the following options regarding his/her Jupyter Notebook: `name`, `namespace`, `cpu`, `memory`, `workspace volume`, `data volumes`, `extra resources`. Notably, he/she can create new Volumes from scratch (type set to `New`) or mount existing ones (type set to `Existing`). By clicking the `SPAWN` button, a new Notebook with the aforementioned options will be created in the `kubeflow` namespace. If some option is not specified, a default value will be used.

**NOTE:**
Please wait for the Notebook Pod to be successfully created and reach Ready state before trying to connect to it.
Otherwise, Ambassador won't be able to route traffic to the correct endpoint and will fail
with "upstream connect error or disconnect/reset before headers".
