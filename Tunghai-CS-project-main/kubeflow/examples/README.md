#### Examples

This example folder contains multiple node-red flow setups, each is isolated with a folder that allows you to run the different examples with the same settings.

##### Add customized npm package

You can add customized npm package via `npm install` or directly modify `packages.json`. Then rebuild your container image.

##### Build

Simply to run the following command to build node-red image

```
./build.sh
```

##### Run the container image

To run the container image, use 

```
KUBEFLOW_HOST=<your-kubeflow-instance-endpoint> \
KUBEFLOW_USERNAME=<your-username-account> \
KUBEFLOW_PASSWORD=<your-password> \
./run.sh <example-args>
```

which would mount the current folder (i.e. ./example) onto the containers. We took this as a convenient step as you could change codes with node-red UI and the mounting volume allows the changes to be reflected onto your local file system.

The example-args allows you to specify which example you want to run, for example

```
./run.sh 0.helloworld
```

would run the `0.helloworld` example.

##### Visit vis UI

then you can go to UI, check it out: http://127.0.0.1:1880/
