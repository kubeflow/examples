import logging
import os
import argparse
import time

import tensorflow as tf
from google.cloud import storage

import models
import preprocess
import metrics


def run_training(args):
    # parse args
    logging.warning('parsing args...')
    model = getattr(models, args.model)(nr_predictors=24, nr_classes=2)
    epochs = args.epochs
    version = args.version
    bucket_name = args.bucket

    # get the data
    logging.warning('getting the data...')
    tickers = ['snp', 'nyse', 'djia', 'nikkei', 'hangseng', 'ftse', 'dax', 'aord']
    closing_data = preprocess.load_data(tickers)
    training_test_data = preprocess.preprocess_data(closing_data)
    training_predictors_tf, training_classes_tf, test_predictors_tf, test_classes_tf = preprocess.train_test_split(
        training_test_data, train_test_ratio=0.8)

    # define training objective
    logging.warning('defining the training objective...')
    sess = tf.Session()
    feature_data = tf.placeholder("float", [None, 24])
    actual_classes = tf.placeholder("float", [None, 2])
    model = model.build_model(feature_data)
    cost = -tf.reduce_sum(actual_classes * tf.log(model))
    train_opt = tf.train.AdamOptimizer(learning_rate=0.0001).minimize(cost)
    init = tf.global_variables_initializer()
    sess.run(init)

    # train model
    correct_prediction = tf.equal(tf.argmax(model, 1), tf.argmax(actual_classes, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))

    logging.warning('training the model...')
    ts = time.time()
    for i in range(1, epochs):
        sess.run(
            train_opt,
            feed_dict={
                feature_data: training_predictors_tf.values,
                actual_classes: training_classes_tf.values.reshape(len(training_classes_tf.values), 2)
            }
        )
        if i % 5000 == 0:
            print(i, sess.run(
                accuracy,
                feed_dict={
                    feature_data: training_predictors_tf.values,
                    actual_classes: training_classes_tf.values.reshape(len(training_classes_tf.values), 2)
                }
            ))
    te = time.time()
    logging.warning('training took {0:.2f} sec'.format(te-ts))

    # print results of confusion matrix
    logging.warning('validating model on test set...')
    feed_dict = {
        feature_data: test_predictors_tf.values,
        actual_classes: test_classes_tf.values.reshape(len(test_classes_tf.values), 2)
    }
    metrics.tf_confusion_metrics(model, actual_classes, sess, feed_dict)

    # create signature for TensorFlow Serving
    logging.warning('Exporting model for tensorflow-serving...')

    export_path = version
    tf.saved_model.simple_save(
        sess,
        export_path,
        inputs={'predictors': feature_data},
        outputs={'prediction': tf.argmax(model, 1), 'model-version': tf.constant([str(version)])}
    )

    # save model on GCS
    logging.warning("uploading to " + bucket_name + "/" + version)
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    if bucket:
        for root, dirs, files in os.walk(export_path):
            for file in files:
                path = os.path.join(root, file)
                blob = bucket.blob(path)
                blob.upload_from_filename(path)


def main():
    parser = argparse.ArgumentParser(description='Training')

    parser.add_argument('--model',
                        type=str,
                        help='model to be used for training',
                        default='DeepModel',
                        choices=['FlatModel', 'DeepModel'])

    parser.add_argument('--epochs',
                        type=int,
                        help='number of epochs to train',
                        default=30000)

    parser.add_argument('--version',
                        type=str,
                        help='version (stored for serving)',
                        default='1')

    parser.add_argument('--bucket',
                        type=str,
                        help='GCS bucket where model is saved',
                        default='saved-models')

    args = parser.parse_args()
    run_training(args)


if __name__ == '__main__':
    logging.info("Starting training")
    main()