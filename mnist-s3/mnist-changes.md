```diff
25a26,27
> import os
> import sys
26a29,36
> # Configure model options
> TF_DATA_DIR = os.getenv("TF_DATA_DIR", "/tmp/data/")
> TF_MODEL_DIR = os.getenv("TF_MODEL_DIR", None)
> TF_EXPORT_DIR = os.getenv("TF_EXPORT_DIR", "mnist/")
> TF_MODEL_TYPE = os.getenv("TF_MODEL_TYPE", "CNN")
> TF_TRAIN_STEPS = int(os.getenv("TF_TRAIN_STEPS", 200))
> TF_BATCH_SIZE = int(os.getenv("TF_BATCH_SIZE", 100))
> TF_LEARNING_RATE = float(os.getenv("TF_LEARNING_RATE", 0.01 ))
70a81,82
>   predict = tf.nn.softmax(logits)
>   classes = tf.cast(tf.argmax(predict, 1), tf.uint8)
79c91
<     return tf.estimator.EstimatorSpec(mode, predictions=predictions)
---
>     return tf.estimator.EstimatorSpec(mode, predictions=predictions, export_outputs={'classes': tf.estimator.export.PredictOutput({"predictions": predict, "classes": classes})})
86c98
<     optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.01)
---
>     optimizer = tf.train.GradientDescentOptimizer(learning_rate=TF_LEARNING_RATE)
97a110,117
> def cnn_serving_input_receiver_fn():
>   inputs = {X_FEATURE: tf.placeholder(tf.float32, [None, 28, 28])}
>   return tf.estimator.export.ServingInputReceiver(inputs, inputs)
> 
> def linear_serving_input_receiver_fn():
>   inputs = {X_FEATURE: tf.placeholder(tf.float32, (784,))}
>   return tf.estimator.export.ServingInputReceiver(inputs, inputs)
> 
103c123
<   mnist = tf.contrib.learn.datasets.DATASETS['mnist']('/tmp/mnist')
---
>   mnist = tf.contrib.learn.datasets.DATASETS['mnist'](TF_DATA_DIR)
107c127
<       batch_size=100,
---
>       batch_size=TF_BATCH_SIZE,
116,131c136,160
<   ### Linear classifier.
<   feature_columns = [
<       tf.feature_column.numeric_column(
<           X_FEATURE, shape=mnist.train.images.shape[1:])]
< 
<   classifier = tf.estimator.LinearClassifier(
<       feature_columns=feature_columns, n_classes=N_DIGITS)
<   classifier.train(input_fn=train_input_fn, steps=200)
<   scores = classifier.evaluate(input_fn=test_input_fn)
<   print('Accuracy (LinearClassifier): {0:f}'.format(scores['accuracy']))
< 
<   ### Convolutional network
<   classifier = tf.estimator.Estimator(model_fn=conv_model)
<   classifier.train(input_fn=train_input_fn, steps=200)
<   scores = classifier.evaluate(input_fn=test_input_fn)
<   print('Accuracy (conv_model): {0:f}'.format(scores['accuracy']))
---
>   if TF_MODEL_TYPE == "LINEAR":
>     ### Linear classifier.
>     feature_columns = [
>         tf.feature_column.numeric_column(
>             X_FEATURE, shape=mnist.train.images.shape[1:])]
> 
>     classifier = tf.estimator.LinearClassifier(
>         feature_columns=feature_columns, n_classes=N_DIGITS, model_dir=TF_MODEL_DIR)
>     classifier.train(input_fn=train_input_fn, steps=TF_TRAIN_STEPS)
>     scores = classifier.evaluate(input_fn=test_input_fn)
>     print('Accuracy (LinearClassifier): {0:f}'.format(scores['accuracy']))
>     #FIXME This doesn't seem to work. sticking to CNN for the example for now.
>     classifier.export_savedmodel(TF_EXPORT_DIR, linear_serving_input_receiver_fn)
>   elif TF_MODEL_TYPE == "CNN":
>     ### Convolutional network
>     training_config = tf.estimator.RunConfig(model_dir=TF_MODEL_DIR, save_summary_steps=100, save_checkpoints_steps=1000)
>     classifier = tf.estimator.Estimator(model_fn=conv_model, model_dir=TF_MODEL_DIR, config=training_config)
>     export_final = tf.estimator.FinalExporter(TF_EXPORT_DIR, serving_input_receiver_fn=cnn_serving_input_receiver_fn)
>     train_spec = tf.estimator.TrainSpec(input_fn=lambda: train_input_fn(), max_steps=TF_TRAIN_STEPS)
>     eval_spec = tf.estimator.EvalSpec(input_fn=lambda: test_input_fn(), steps=1, exporters=export_final, throttle_secs=1,
>                                       start_delay_secs=1)
>     tf.estimator.train_and_evaluate(classifier, train_spec, eval_spec)
>   else:
>     print("No such model type: %s" % TF_MODEL_TYPE)
>     sys.exit(1)
```
