import kfp
from kfp import dsl
from kfp.components import func_to_container_op
from kubernetes.client.models import V1ContainerPort

def server():
    import json
    import pandas as pd
    import numpy as np
    import pickle
    import threading
    import time
    import tensorflow as tf
    from flask import Flask, jsonify,request
    import os
    
    app = Flask(__name__)
    clients_local_count = []
    scaled_local_weight_list = []
    global_value = { #Share variable
                    'last_run_statue' : False, #last run finish or not
                    'data_statue' : None,      #global_count finish or not
                    'global_count' : None,
                    'scale_statue' : None,
                    'weight_statue' : None,
                    'average_weights' : None,
                    'shutdown' : 0}
    
    NUM_OF_CLIENTS = 2 #number of clients
    
    init_lock = threading.Lock()
    clients_local_count_lock = threading.Lock()
    scaled_local_weight_list_lock = threading.Lock()
    cal_weight_lock = threading.Lock()
    shutdown_lock = threading.Lock()
    
    @app.before_request
    def before_request():
        print('get request')
        
        
    @app.route('/data', methods=['POST'])
    def flask_server():
        with init_lock:  #check last run is finish and init varible
            
            while True:
                
                if(len(clients_local_count)==0 and global_value['last_run_statue'] == False):#init the variable by first client enter
                    global_value['last_run_statue'] = True
                    global_value['data_statue'] = False
                    global_value['scale_statue'] = False
                    global_value['weight_statue'] = False
                    break
                
                elif(global_value['last_run_statue'] == True):
                    break
                time.sleep(3)
        
        local_count = int(request.form.get('local_count'))          #get data
        bs = int(request.form.get('bs'))
        local_weight = json.loads(request.form.get('local_weight'))
        local_weight = [np.array(lst) for lst in local_weight]
        

        
        
        def scale_model_weights(weight, scalar):
            weight_final = []
            steps = len(weight)
            for i in range(steps):
                weight_final.append(scalar * weight[i])
            return weight_final
        def sum_scaled_weights(scaled_weight_list):
            
            avg_grad = list()
            #get the average grad accross all client gradients
            for grad_list_tuple in zip(*scaled_weight_list):
                layer_mean = tf.math.reduce_sum(grad_list_tuple, axis=0)
                avg_grad.append(layer_mean)

            return avg_grad
        
        with clients_local_count_lock:
            clients_local_count.append(int(local_count))
            
        with scaled_local_weight_list_lock:
            while True:
                
                if (len(clients_local_count) == NUM_OF_CLIENTS and global_value['data_statue'] != True):
                    global_value['last_run_statue'] = False
                    sum_of_local_count=sum(clients_local_count)
                    
                    
                    global_value['global_count'] = sum_of_local_count     
                    
                    scaling_factor=local_count/global_value['global_count']
                    scaled_weights = scale_model_weights(local_weight, scaling_factor)
                    scaled_local_weight_list.append(scaled_weights)
                    
                    global_value['scale_statue'] = True 
                    global_value['data_statue'] = True
                    break
                elif (global_value['data_statue'] == True and global_value['scale_statue'] == True):
                    scaling_factor=local_count/global_value['global_count']
                    scaled_weights =scale_model_weights(local_weight, scaling_factor)
                    scaled_local_weight_list.append(scaled_weights)
        
                    break
                time.sleep(1)
               
        with cal_weight_lock:
            
            while True:
                if(len(scaled_local_weight_list) == NUM_OF_CLIENTS and global_value['weight_statue'] != True):
                    
                    global_value['average_weights'] = sum_scaled_weights(scaled_local_weight_list)
                    global_value['weight_statue'] = True
                    global_value['average_weights'] = json.dumps([np.array(w).tolist() for w in global_value['average_weights']])
                    
                    break
                    
                elif(global_value['weight_statue'] == True):
                    
                    break
                
                time.sleep(1)
                
                
        clients_local_count.clear()
        scaled_local_weight_list.clear()
        
        return jsonify({'result': (global_value['average_weights'])})
        
    
    @app.route('/shutdown', methods=['GET'])
    def shutdown_server():
        global_value['shutdown'] +=1 
        with shutdown_lock:
            while True:
                if(global_value['shutdown'] == NUM_OF_CLIENTS):
                    os._exit(0)
                    return 'Server shutting down...'
                time.sleep(1)
    
    
    app.run(host="0.0.0.0", port=8080)


def client(batch:int) :
    import json
    import requests
    import time
    import pandas as pd
    import numpy as np
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Conv1D
    from tensorflow.keras.layers import MaxPooling1D
    from tensorflow.keras.layers import Activation
    from tensorflow.keras.layers import Flatten
    from tensorflow.keras.layers import Dense
    from tensorflow.keras.optimizers import SGD
    from tensorflow.keras import backend as K

    normal_url='<change yourself>' 
    abnormal_url='<change yourself>'
    normal_data = pd.read_csv(normal_url)
    abnormal_data = pd.read_csv(abnormal_url)
    num_features = len(normal_data.columns)
    print(num_features)
    normal_label = np.array([[1, 0]] * len(normal_data))
    abnormal_label = np.array([[0, 1]] * len(abnormal_data))
    
    
    data = np.vstack((normal_data, abnormal_data))
    data_label = np.vstack((normal_label, abnormal_label))

    
    shuffler = np.random.permutation(len(data))
    data = data[shuffler]
    data_label = data_label[shuffler]

    
    data = data.reshape(len(data), num_features, 1)
    data_label = data_label.reshape(len(data_label), 2)

   
    full_data = list(zip(data, data_label))
    data_length=len(full_data)
    
    class SimpleMLP:
        @staticmethod
        def build(shape, classes):
            model = Sequential()
            model.add(Conv1D(filters=4, kernel_size=3, input_shape=(17,1)))
            model.add(MaxPooling1D(3))
            model.add(Flatten())
            model.add(Dense(8, activation="relu"))
            model.add(Dense(2, activation = 'softmax'))

            return model
    
    
    if(batch==1):
        full_data=full_data[0:int(data_length/2)] #batch data
    else:
        full_data=full_data[int(data_length/2):data_length] #The client should have its own data, not like this. It's a lazy method.
    
    print('data len= ',len(full_data))
    def batch_data(data_shard, bs=32):
    
        #seperate shard into data and labels lists
        data, label = zip(*data_shard)
        dataset = tf.data.Dataset.from_tensor_slices((list(data), list(label)))
        return dataset.shuffle(len(label)).batch(bs)
    
    dataset=batch_data(full_data)
    #print(dataset)
    
    bs = next(iter(dataset))[0].shape[0]
    local_count = tf.data.experimental.cardinality(dataset).numpy()*bs
    
    
    loss='categorical_crossentropy'
    metrics = ['accuracy']
    optimizer = 'adam'
    
    
    smlp_model = SimpleMLP()
    
    server_url="http://http-service:5000/data"
    for comm_round in range(5):
        print('The ',comm_round+1, 'round')
        client_model = smlp_model.build(17, 1)
        client_model.compile(loss=loss, 
                      optimizer=optimizer, 
                      metrics=metrics)
        
        if(comm_round == 0):
            history = client_model.fit(dataset, epochs=50, verbose=1)
        else:
            client_model.set_weights(avg_weight)
            history = client_model.fit(dataset, epochs=50, verbose=1)
        
        local_weight = client_model.get_weights()
        local_weight = [np.array(w).tolist() for w in local_weight]
        
        client_data = {"local_count": local_count,'bs': bs, 'local_weight': json.dumps(local_weight)}
        
        while True:
            try:
                weight = (requests.post(server_url,data=client_data))
                
                if weight.status_code == 200:
                    print(f"exist")

                    break
                else:
                    print(f"server error")

            except requests.exceptions.RequestException:

                print(f"not exist")
                
            time.sleep(5)
            
        data = weight.json()
        avg_weight = data.get('result')
        avg_weight = json.loads(avg_weight)
        avg_weight = [np.array(lst) for lst in avg_weight]
        
    shutdown_url="http://http-service:5000/shutdown"    
    try:
        response = requests.get(shutdown_url)
    except requests.exceptions.ConnectionError:
        print('already shutdown')


server_op=func_to_container_op(server,base_image='tensorflow/tensorflow',packages_to_install=['flask','pandas'])
client_op=func_to_container_op(client,base_image='tensorflow/tensorflow',packages_to_install=['requests','pandas'])
@dsl.pipeline(
    name='FL test'
    )
def fl_pipeline(namespace='kubeflow-user-thu01'):
    
    service = dsl.ResourceOp(
        name='http-service',
        k8s_resource={
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': 'http-service'
            },
            'spec': {
                'selector': {
                    'app': 'http-service'
                },
                'ports': [
                    {
                        'protocol': 'TCP',
                        'port': 5000,
                        'targetPort': 8080
                    }
                ]
            }
        }
    )#service_end
    server_task=server_op()
    server_task.add_pod_label('app', 'http-service')
    server_task.add_port(V1ContainerPort(name='my-port', container_port=8080))
    server_task.set_cpu_request('0.2').set_cpu_limit('0.2')
    server_task.after(service)
    
    client_task_1=client_op(1)
    client_task_1.set_cpu_request('0.2').set_cpu_limit('0.2')
    clienttask_2=client_op(2)
    clienttask_2.set_cpu_request('0.2').set_cpu_limit('0.2')
    
    delete_service = dsl.ResourceOp(
        name='delete-service',
        k8s_resource={
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': 'http-service'
            },
            'spec': {
                'selector': {
                    'app': 'http-service'
                },
                'ports': [
                    {
                        'protocol': 'TCP',
                        'port': 80,
                        'targetPort': 8080
                    }
                ],
                'type': 'NodePort'  
            }
        },
        action="delete" #delete
    ).after(server_task)



if __name__ == '__main__':
    kfp.compiler.Compiler().compile(fl_pipeline, 'fl_pipeline.yaml')
