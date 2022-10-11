# Transfer_learning_Template-application
This repo. Is intended for constructing a pipeline template for transfer learning applications.  Transfer learning is a technique which allows replacing of the hidden layer parameters in an AI training process where the input sample size is small.  The outcome of the training results from a small sample size is generally either biased or performs badly.  This repo. Introduces a template construct which allows the replacement action from a large data set such as Vgg-16 or Resnet.  Users don’t have to rewrite the transfer learning code and replace the big data hidden layers  manually.  After the transfer learning template is developed, it can be uploaded and shared on the Kubeflow pipeline UI.  A Pipelines component is a set of independent user code, packaged as a Docker image, that executes a step in a pipeline. For example, a component can be responsible for data preprocessing, data transformation, model training, etc., implemented as a Kubernetes CRD (Custom Resource Definition). So workflows can be managed using kubectl and integrated with other Kubernetes services such as volumes, secrets, and RBAC.
The test data set used in this repo. Is from voice speech recognition application.  The voice patterns of three persons is converted in frequency spectrum via fourier transformation as the following example.

The transformed spectrum is reduced to a 100*100 image as shown below.  There are three categories of images from three different persons.  An eight twenty ratio of data division is used for training and testing of the proposed transfer learning template examples.  

![image](https://user-images.githubusercontent.com/89516000/195132853-29e6a45d-2e53-44c3-b2a1-e649510033b2.png)
![image](https://user-images.githubusercontent.com/89516000/195132872-fae7fd6b-de8f-4b15-b641-4673decbc965.png)

The following are steps to construct the transfer learning template pipeline.
1.	Load the required package, define the required version through requirements.txt and run it.

![image](https://user-images.githubusercontent.com/89516000/195132895-75c3b470-f0cf-4d3c-ae40-71247aac6d2b.png)

2. The established pipeline diagram, using transfer learning, divides the model into three components.  They are divided into input data, model and output parts. The entire pipeline flow is divided into the parts of establishment, model input layer, and data training.
3. The pipeline establishment process is to extract the training data first, and use two parameters (data_path, model_file) to load the dataset required by the model which are the directory where the original data is located, and the file name of the model respectively.  We use data_path to read the files needed.  It is revealed through built-in jupyter editor of Kubeflow.  All data can be run locally, and it is also convenient to find the data path for training when the model is loaded in later use.
 
![image](https://user-images.githubusercontent.com/89516000/195132921-618ebf18-1f4b-4ca2-958d-c5a42a6772c2.png)

4.Then enter the data training stage, use the migration learning of CNN to process the data, first establish a preliminary CNN model, set the top input layer (include_top) to false (remove the input layer to fit into our input part), this Indicates that the VGG16 model will be loaded, excluding the convolutional layers added to the last 3 layers in order to obtain Features.  After the model is built, iterate 10 times to process the input data.

![image](https://user-images.githubusercontent.com/89516000/195132946-ee44f391-ab84-49e3-90ad-bf63f2cf4112.png)

5. Go to predict components and load my original data path (data_path) and model (model_file) to make predictions.

![image](https://user-images.githubusercontent.com/89516000/195132995-c6dc82c8-ff83-4898-a5f8-8bca0da569d0.png)

6. Next start to build the workflow.  load the components of train and predict into a container, use the function to convert it into a container to package it to build the data. Here, the parameters are the components of train and predict.  The formed image is then used to run all future operations.

![image](https://user-images.githubusercontent.com/89516000/195133037-657498b9-072d-4031-aaab-6329c875ecdd.png)

7.This step package the image and configure the running status of the pipeline. The sequence is the input of the training model -> model -> training result.  I configure the generated image to /mnt/ of the built-in jupyter, so the path to the pipeline is also required.  The specified data_path is in /mnt/ in order to bring out the trained data, the model trained file is also generated in this path (tf_model.h5), and the predicted image name (0.jpg), in order to establish a working pipeline . Finally, compile the pipeline, package it into yaml and execute it.
 
![image](https://user-images.githubusercontent.com/89516000/195133085-0247d840-5c44-4a28-93af-ef9ecaeefe39.png)
![image](https://user-images.githubusercontent.com/89516000/195133107-d0c43393-8a93-4ccc-8d7a-2ac950ccd306.png)

8. The complete cycle is a set of pipelines with migration learning as a template. The model components are used to wrap the input layer of the model, and the model can also be replaced with a model based on keras (ex. Caffe, PyTorch, TensorFlow) for training.  The purpose is to apply the data to the trained model, set the image path and the path to generate the mirror image, and realize the deployment of various machine learning on the pipeline.

![image](https://user-images.githubusercontent.com/89516000/195133169-7260eae7-b761-4be3-ac9a-6121bd3ba02d.png)

9.	The generated yaml file is used to package the model and the training template. Our model has been compiled into an image and packaged.  The generated file is uploaded to the pipeline for execution.
 
![image](https://user-images.githubusercontent.com/89516000/195133204-7af28767-c99d-44fc-844a-f70783e54d77.png)
![image](https://user-images.githubusercontent.com/89516000/195133219-4e2f65ea-fa56-4f56-9087-7321f2736de9.png)

10. The output data is presented in the pod in the form of training, and 10 batches are repeated to process the images, and then the trained information is stored in tf_model.h5.

![image](https://user-images.githubusercontent.com/89516000/195133259-979ba97d-45f4-4145-bc01-c4e0527da33c.png)

11. Create a yaml file with pipeline components and output it to kubeflow for k8s as a container orchestration subordinate, and use minikube CLI to view pod logs on the local side.

![image](https://user-images.githubusercontent.com/89516000/195133300-e00628d5-fddf-404a-be0b-ce5d4c222be8.png)
