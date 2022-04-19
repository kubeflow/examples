from tensorflow.keras.models import load_model
import autokeras as ak
import pandas as pd
import numpy as np

### Load model 
loaded_model = load_model("/data/model_autokeras", custom_objects=ak.CUSTOM_OBJECTS)

### Pint model summary
print(loaded_model.summary())

test_dir='/data/test.csv'
test=pd.read_csv(test_dir)

X_test=[]
for img in test['Image']:
    X_test.append(np.asarray(img.split(),dtype=float).reshape(96,96,1))
X_test=np.reshape(X_test,(-1,96,96,1))
X_test = np.asarray(X_test).astype('float32')

### predict 
y_pred = loaded_model.predict(X_test)

### Create submission file
y_pred= y_pred.reshape(-1,)
submission = pd.DataFrame({'Location': y_pred})
submission.to_csv('/data/submission.csv', index=True , index_label='RowId')

