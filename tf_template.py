#!/usr/bin/env python
# coding: utf-8

# In[1]:


with open("requirements.txt", "w") as f:
    f.write("kfp==1.8.9\n")
get_ipython().system('pip install -r requirements.txt  --upgrade --user')


# In[2]:


import kfp
import kfp.dsl as dsl
import kfp.components as comp


# In[6]:


def train(data_path,model_file):
    import numpy as pd
    from tensorflow import keras
    from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array, array_to_image 
    from tensorflow.keras.layers import Conv2D, Flatten, MaxPooling2D, Dense
    from tensorflow.keras.models import Sequential  
    from keras.applications import VGG16

    root_path = data_path
    
    train_datagen = ImageDataGenerator(
        rescale=1. / 225,
        shear_range=0.1,
        zoom_range=0.1,
        width_shift_range=0.1,
        height__shift_range=0.1,
        horizontal_flip=True,
        vertical_flip = True,
        validation_split = 0.1
     )
    
    val_datagen = ImageDataGenerator(
        rescale=1. / 225,
        validation_split = 0.1)
    
    train_generator = train_datagen.flow_from_directory(
        root_path+'dataset',
        target_size=(300, 300),
        batch_size=8,
        class_mode='categorical',
        subset='training',
        seed=0)
    
    model = Sequential()  



    model = VGG16(weights='imagenet', include_top=false)     
    model.add(Conv2D(filters=32, kernel_size=3, padding='same', input_shape=(300, 300, 3), activation='relu')) 
    model.add(MaxPooling2D(pool_size=2))  

    model.add(Conv2D(filters=64, kernel_size=3, padding='same', activation='relu'))  
    model.add(MaxPooling2D(pool_size=(2,2)))  

    model.add(Conv2D(filters=64, kernel_size=3, padding='same', activation='relu'))  
    model.add(MaxPooling2D(pool_size=(2,2)))  

    model.add(Conv2D(filters=64, kernel_size=3, padding='same', activation='relu'))  
    model.add(MaxPooling2D(pool_size=(2,2)))  
    model.add(Flatten())
    
    
    model.add(Dense(64, activation='relu'))
    model.add(Dense(6, activation='softmax'))

    model.summary()
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])  

    import time
    start_time = time.time()
    
    history = model.fit(train_generator,
                        epochs=10,
                        steps_per_epoch=2276//32,
                        validation_data=val_generator,
                        validation_steps=251//32)
    end_time = time.time()
    
    print('time',end - start,' s')
    
    model.save(root_path+model_file)
    print('model save')
    
def model_op():
  return dsl.ContainerOp(
      name='model',
      image='library/bash:4.4.23',
      command=['sh', '-c'],
      arguments=['echo "$0"'])    


# In[7]:


def predict(data_path, model_file, test_file):
    import tensorflow as tf
    import numpy as np
    from tensorflow.keras.perprocessing import image
    label = {0: '0',1: '1',2: '2',3: '3'}
    
    
    model = tf.keras.models.load_model(data_path+model_file)
    
    
    
    img_path = data_path + test_file
    img = image.load_img(img_path, target_size(300,300))
    img = image.img_to_array(img)
    img = np.expend_dims(img,axis=0)
    result = model.predict(img)
    
    def generate_result(result):
        for i in range(6):
            if(result[0][i] == 1):
                return label[i]
        print(generate_result(result))


# In[8]:


train_op = comp.func_to_container_op(func=train,base_image='tensorflow/tensorflow:2.0.0-py3',)
predict_op = comp.func_to_container_op(func=predict,base_image='tensorflow/tensorflow:2.0.0-py3',)


# In[9]:


import kfp.dsl as dsl
import kfp.components as components
 
@dsl.pipeline(
   name='tf pipeline',
   description='A pipeline to train a model dataset.'
)

def tf_container_pipeline(
    data_path: str,
    model_file: str,
    test_path: str,
    text1=' '
):

    vop = dsl.PipelineVolume(pvc="")
    training_container = train_op(data_path, model_file).add_pvolumes({data_path: vop})

    predict_container = predict_op(data_path, model_file, test_path).add_pvolumes({data_path: training_container.pvolume})
    

    step1_task = model_op(text1)
    step1_task.after(training_container)
    predict_container.after(step1_task)
    


# In[10]:


DATA_PATH = '/mnt/'
MODEL_PATH='tf_model.h5'
TEST_PATH='0.jpg'

pipeline_func = tf_container_pipeline

experiment_name = 'tf_kubeflow'
run_name = pipeline_func.__name__+ 'run'

arguments = {"data_path":DATA_PATH,
             "model_file":MODEL_PATH,
             "test_path":TEST_PATH}


# In[11]:


kfp.compiler.Compiler().compile(tf_container_pipeline, 'helloworld.zip')


# In[ ]:




