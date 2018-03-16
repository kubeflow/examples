```diff
41a42
> import os
48a50,51
> flags.DEFINE_string("train_dir", "/tmp/mnist-train",
>                     "Directory for training output")
81a85,86
> flags.DEFINE_string("master_hosts", "",
>                     "Comma-separated list of hostname:port pairs")
87a93,120
> def mnist_inference(hidden_units):
>     # Variables of the hidden layer
>     hid_w = tf.Variable(
>         tf.truncated_normal(
>             [IMAGE_PIXELS * IMAGE_PIXELS, FLAGS.hidden_units],
>             stddev=1.0 / IMAGE_PIXELS),
>         name="hid_w")
>     hid_b = tf.Variable(tf.zeros([FLAGS.hidden_units]), name="hid_b")
> 
>     # Variables of the softmax layer
>     sm_w = tf.Variable(
>         tf.truncated_normal(
>             [FLAGS.hidden_units, 10],
>             stddev=1.0 / math.sqrt(FLAGS.hidden_units)),
>         name="sm_w")
>     sm_b = tf.Variable(tf.zeros([10]), name="sm_b")
> 
>     # Ops: located on the worker specified with FLAGS.task_id
>     x = tf.placeholder(tf.float32, [None, IMAGE_PIXELS * IMAGE_PIXELS])
>     y_ = tf.placeholder(tf.float32, [None, 10])
> 
>     hid_lin = tf.nn.xw_plus_b(x, hid_w, hid_b)
>     hid = tf.nn.relu(hid_lin)
> 
>     y = tf.nn.softmax(tf.nn.xw_plus_b(hid, sm_w, sm_b))
>     cross_entropy = -tf.reduce_sum(y_ * tf.log(tf.clip_by_value(y, 1e-10, 1.0)))
> 
>     return x, y, y_, cross_entropy
90a124
> 
104a139
>   master_spec = FLAGS.master_hosts.split(",")
109c144,151
<   cluster = tf.train.ClusterSpec({"ps": ps_spec, "worker": worker_spec})
---
>   cluster_specc = {"ps": ps_spec, "worker": worker_spec}
>   print("cluster_specc = %s" % str(cluster_specc))
>   print("num_workers = %d" % num_workers)
> 
>   if FLAGS.master_hosts == "":
>     cluster = tf.train.ClusterSpec({"ps": ps_spec, "worker": worker_spec})
>   else:
>     cluster = tf.train.ClusterSpec({"master": master_spec, "ps": ps_spec, "worker": worker_spec})
115a158
>       print("Running ps.")
118c161
<   is_chief = (FLAGS.task_id == 0)
---
>   is_chief = (FLAGS.task_id == 0) # and (FLAGS.job_name == "master")
138,162c181
<     # Variables of the hidden layer
<     hid_w = tf.Variable(
<         tf.truncated_normal(
<             [IMAGE_PIXELS * IMAGE_PIXELS, FLAGS.hidden_units],
<             stddev=1.0 / IMAGE_PIXELS),
<         name="hid_w")
<     hid_b = tf.Variable(tf.zeros([FLAGS.hidden_units]), name="hid_b")
< 
<     # Variables of the softmax layer
<     sm_w = tf.Variable(
<         tf.truncated_normal(
<             [FLAGS.hidden_units, 10],
<             stddev=1.0 / math.sqrt(FLAGS.hidden_units)),
<         name="sm_w")
<     sm_b = tf.Variable(tf.zeros([10]), name="sm_b")
< 
<     # Ops: located on the worker specified with FLAGS.task_id
<     x = tf.placeholder(tf.float32, [None, IMAGE_PIXELS * IMAGE_PIXELS])
<     y_ = tf.placeholder(tf.float32, [None, 10])
< 
<     hid_lin = tf.nn.xw_plus_b(x, hid_w, hid_b)
<     hid = tf.nn.relu(hid_lin)
< 
<     y = tf.nn.softmax(tf.nn.xw_plus_b(hid, sm_w, sm_b))
<     cross_entropy = -tf.reduce_sum(y_ * tf.log(tf.clip_by_value(y, 1e-10, 1.0)))
---
>     x, y, y_, cross_entropy = mnist_inference(FLAGS.hidden_units)
192c211,216
<     train_dir = tempfile.mkdtemp()
---
> 
>     try:
>       os.makedirs(FLAGS.train_dir)
>     except OSError:
>       if not os.path.isdir(FLAGS.train_dir):
>         raise
197c221
<           logdir=train_dir,
---
>           logdir=FLAGS.train_dir,
206c230
<           logdir=train_dir,
---
>           logdir=FLAGS.train_dir,
243a268,269
>     sess.graph._unsafe_unfinalize()
>     saver = tf.train.Saver(max_to_keep=None)
259c285
< 
---
>     saver.save(sess, FLAGS.train_dir)
```
