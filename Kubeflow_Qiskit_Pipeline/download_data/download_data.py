import json
import argparse
import numpy as np
from pathlib import Path
from tensorflow import keras

def _download_data(args):
    (x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()
    
    idx_train = np.append(
    np.where(y_train == 0)[0][:100], np.where(y_train == 1)[0][:100]
    )
    x_train = x_train[idx_train]
    y_train = y_train[idx_train]


    idx_test = np.append(
        np.where(y_test == 0)[0][:50], np.where(y_test == 1)[0][:50]
    )

    x_test = x_test[idx_test]
    y_test = y_test[idx_test]
    
    train_data=x_train
    test_data=x_test
    train_label=y_train
    test_label=y_test
    data = {'x_train' : train_data.tolist(),
            'y_train' : train_label.tolist(),
            'x_test' : test_data.tolist(),
            'y_test' : test_label.tolist() }
    
    data_json = json.dumps(data)
    with open(args.data, 'w') as out_file:
        json.dump(data_json, out_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str)
    parser.add_argument('--data', type=str)
    args = parser.parse_args()

    
    Path(args.data).parent.mkdir(parents=True, exist_ok=True)

    _download_data(args)
    
    