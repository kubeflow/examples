#!/usr/bin/env python
# coding: utf-8

# In[34]:


def trainOp(model_relative_path: str = 'model', model_name: str = 'resnet_graphdef'):

    import pathlib
    import os
    
    home = '/home/'
    output_model_dir = os.path.join(home, model_relative_path)
    model_dir = os.path.join(output_model_dir, model_name)
    
    pathlib.Path(model_dir).mkdir(parents=True, exist_ok=True)
    
    from tintin.online_serving import save_function_to_model
    from tintin.online_serving import transform_data_file_name
    @save_function_to_model(model_path=output_model_dir, file_name=transform_data_file_name)
    def transform_data(input_data):
        from tensorflow.keras.applications import VGG16
        conv_base = VGG16(weights='imagenet',
                          include_top=False,
                          input_shape=(100,100, 3))
    
        return input_data


# In[35]:


with open("requirements.txt", "w") as f:
    f.write("kfp==0.5.1\n")
    f.write("h5py<3.0.0\n")
    f.write("tintin-sdk>=0.0.4\n")
    f.write("tensorflow>=2.0.0\n")

get_ipython().system('pip install -r requirements.txt --user --upgrade')


# In[36]:


import kfp
import kfp.dsl as dsl
import kfp.components as comp
import kfp.compiler as compiler


# In[37]:


import os
pvcname = os.environ.get('tf')
generated_pipeline_zip_filename = os.environ.get('tf')
gpu_type_list_text = os.environ.get('TINTIN_SESSION_TEMPLATE_GPU_TYPE_LIST')
default_image = os.environ.get('TINTIN_SESSION_TEMPLATE_DEFAULT_IMAGE', 'footprintai/nvidia-tensorflow:19.12-tf1-py3')
mountPath = os.environ.get(' ', '/home/')


# In[39]:


trainComp = comp.func_to_container_op(trainOp, 
                                      base_image=default_image,
                                      packages_to_install=["tintin-sdk>=0.0.4"])

import kfp.dsl as dsl
@dsl.pipeline(
   name='template pipeline',
   description='pipeline'
)
def templated_pipeline_func(
):
    
    model_relative_path = os.environ.get(' ', 'model')    
    model_name = os.environ.get('tf', 'resnet_graphdef')
    
    train_task = trainComp(model_relative_path, model_name)
    train_task = train_task.add_resource_request('cpu', '1')
    train_task = train_task.add_resource_limit('cpu', '1')
    train_task = train_task.add_resource_request('memory', '4Gi')
    train_task = train_task.add_resource_limit('memory', '4Gi')
    
    train_task = train_task.add_pod_annotation(' ', model_relative_path)    
    train_task = train_task.add_pod_annotation(' ', model_name)
kfp.compiler.Compiler().compile(templated_pipeline_func, "template.zip")


# In[ ]:





# In[ ]:




