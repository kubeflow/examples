'''
Copyright 2018 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''


import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

import ngraph_bridge # pylint: disable=W0611


###############################################################
#   SETUP
###############################################################

# define input arguments
tf.app.flags.DEFINE_string('version', '1',
                           'model version')
tf.app.flags.DEFINE_string('bucket', None,
                           'name of the GCS bucket')
tf.app.flags.DEFINE_integer('steps', 2000,
                            'number of runs through entire training set')
arg_version = tf.app.flags.FLAGS.version
arg_bucket = tf.app.flags.FLAGS.bucket
arg_steps = tf.app.flags.FLAGS.steps

# network parameters
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
feature_size = 784
num_classes = 10
hidden_size = feature_size - 100
hidden_size2 = hidden_size - 100
batch_size = 50
learning_rate = 1e-4


###############################################################
#   BUILD THE GRAPH
###############################################################

def create_layer(shape, prev_layer, is_output):
  W = tf.Variable(tf.truncated_normal(shape, stddev=0.1))
  b = tf.Variable(tf.constant(0.1, shape=[shape[1]]))
  activation = tf.matmul(prev_layer, W) + b
  if is_output:
    new_layer = tf.nn.softmax(activation)
  else:
    new_layer = tf.nn.relu(activation)
    tf.nn.dropout(new_layer, dropout_prob)
  return new_layer


# define inputs
x = tf.placeholder(tf.float32, [None, feature_size], name='x-input')
y = tf.placeholder(tf.float32, [None, num_classes], name='y-input')
dropout_prob = tf.placeholder(tf.float32)

# define layer structure
layer1 = create_layer([feature_size, hidden_size], x, False)
layer2 = create_layer([hidden_size, hidden_size2], layer1, False)
outlayer = create_layer([hidden_size2, num_classes], layer2, True)
prediction = tf.argmax(outlayer, 1)

# training ops
total_cost = -tf.reduce_sum(y * tf.log(outlayer), reduction_indices=[1])
mean_cost = tf.reduce_mean(total_cost)
train = tf.train.AdamOptimizer(learning_rate).minimize(mean_cost)

# accuracy ops
correct_prediction = tf.equal(prediction, tf.argmax(y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

###############################################################
#   TRAIN
###############################################################

sess = tf.Session()
init = tf.global_variables_initializer()
sess.run(init)

for i in range(arg_steps):
  batch_x, batch_y = mnist.train.next_batch(batch_size)
  feed_dict = {x: batch_x, y: batch_y, dropout_prob: 0.5}
  sess.run(train, feed_dict=feed_dict)
  if i % 100 == 0:
    feed_dict = {x: batch_x, y: batch_y, dropout_prob: 0.5}
    train_acc = sess.run(accuracy, feed_dict=feed_dict)
    print("step %d/%d, training accuracy %g" % (i, arg_steps, train_acc))
# print final accuracy on test images
feed_dict = {x: mnist.test.images, y: mnist.test.labels, dropout_prob: 1.0}
print(sess.run(accuracy, feed_dict=feed_dict))

###############################################################
#   EXPORT TRAINED MODEL
###############################################################

# create signature for TensorFlow Serving
tensor_info_x = tf.saved_model.utils.build_tensor_info(x)
tensor_info_pred = tf.saved_model.utils.build_tensor_info(prediction)
tensor_info_scores = tf.saved_model.utils.build_tensor_info(outlayer)
tensor_info_ver = tf.saved_model.utils.build_tensor_info(tf.constant([str(arg_version)]))
prediction_signature = (tf.saved_model.signature_def_utils.build_signature_def(
        inputs={'images': tensor_info_x},
        outputs={'prediction': tensor_info_pred, 'scores': tensor_info_scores,
                 'model-version': tensor_info_ver},
        method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME))
legacy_init_op = tf.group(tf.tables_initializer(), name='legacy_init_op')

print("saving model locally")
# save model to disk
export_path = arg_version
builder = tf.saved_model.builder.SavedModelBuilder(export_path)
builder.add_meta_graph_and_variables(
      sess, [tf.saved_model.tag_constants.SERVING],
      signature_def_map={
           'predict_images': prediction_signature
      },
      legacy_init_op=legacy_init_op)
builder.save()
print("writing pbtxt")
tf.train.write_graph(sess.graph_def, '/home/tensorflow', 'saved_model.pbtxt')
